using System;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using ClashGuardRevit.Models;

namespace ClashGuardRevit.Collectors
{
    /// <summary>
    /// Collects and extracts MEP + Architecture elements.
    /// All output coordinates and dimensions are in millimeters.
    /// </summary>
    public class MepElementCollector
    {
        // Conversion: 1 Revit foot = 304.8 mm
        private const double FeetToMm = 304.8;

        // ── MEP Categories ───────────────────────────────────────────────
        private static readonly BuiltInCategory[] MepCategories = new[]
        {
            // Ducts
            BuiltInCategory.OST_DuctCurves,
            BuiltInCategory.OST_FlexDuctCurves,
            BuiltInCategory.OST_DuctFitting,
            BuiltInCategory.OST_DuctAccessory,

            // Pipes
            BuiltInCategory.OST_PipeCurves,
            BuiltInCategory.OST_FlexPipeCurves,
            BuiltInCategory.OST_PipeFitting,
            BuiltInCategory.OST_PipeAccessory,

            // Conduit & Cable Tray
            BuiltInCategory.OST_Conduit,
            BuiltInCategory.OST_ConduitFitting,
            BuiltInCategory.OST_CableTray,
            BuiltInCategory.OST_CableTrayFitting,

            // Equipment & Fixtures
            BuiltInCategory.OST_MechanicalEquipment,
            BuiltInCategory.OST_PlumbingFixtures,
            BuiltInCategory.OST_FireProtection,         // Sprinklers
            BuiltInCategory.OST_ElectricalEquipment,
            BuiltInCategory.OST_ElectricalFixtures,
            BuiltInCategory.OST_LightingFixtures,
        };

        // ── Architecture Categories ──────────────────────────────────────
        private static readonly BuiltInCategory[] ArchCategories = new[]
        {
            BuiltInCategory.OST_Walls,
            BuiltInCategory.OST_Doors,
            BuiltInCategory.OST_Windows,
            BuiltInCategory.OST_Floors,
            BuiltInCategory.OST_Ceilings,
            BuiltInCategory.OST_Roofs,
            BuiltInCategory.OST_StructuralFraming,      // Beams
            BuiltInCategory.OST_StructuralColumns,
            BuiltInCategory.OST_StructuralFoundation,
            BuiltInCategory.OST_Stairs,
            BuiltInCategory.OST_Ramps,
        };

        private readonly Document _doc;

        public MepElementCollector(Document doc)
        {
            _doc = doc ?? throw new ArgumentNullException(nameof(doc));
        }

        // ── Public Entry Point ───────────────────────────────────────────

        public MepCollectionResult Collect()
        {
            var result = new MepCollectionResult
            {
                ModelName = _doc.Title,
                ModelPath = _doc.PathName
            };

            foreach (var cat in MepCategories)
                CollectByCategory(cat, "MEP", result.Elements);

            foreach (var cat in ArchCategories)
                CollectByCategory(cat, "Architecture", result.Elements);

            // Counts
            result.TotalCount = result.Elements.Count;
            result.MepCount = result.Elements.FindAll(e => e.ElementType == "MEP").Count;
            result.ArchCount = result.Elements.FindAll(e => e.ElementType == "Architecture").Count;

            return result;
        }

        // ── Collection ───────────────────────────────────────────────────

        private void CollectByCategory(BuiltInCategory category,
                                       string elementType,
                                       List<MepElementData> target)
        {
            var collector = new FilteredElementCollector(_doc)
                .OfCategory(category)
                .WhereElementIsNotElementType();

            foreach (Element elem in collector)
            {
                var data = ExtractElementData(elem, category, elementType);
                if (data != null)
                    target.Add(data);
            }
        }

        // ── Extraction ───────────────────────────────────────────────────

        private MepElementData ExtractElementData(Element elem,
                                                  BuiltInCategory category,
                                                  string elementType)
        {
            try
            {
                BoundingBoxXYZ bb = elem.get_BoundingBox(null);
                if (bb == null)
                    return null;

                var data = new MepElementData
                {
                    ElementId = elem.Id.Value,
                    Category = category.ToString().Replace("OST_", ""),
                    ElementType = elementType,
                    FamilyName = ResolveFamilyName(elem),
                    TypeName = ResolveTypeName(elem),
                    LevelName = ResolveLevelName(elem),
                    WorksetName = ResolveWorksetName(elem),
                    Mark = ResolveStringParam(elem, BuiltInParameter.ALL_MODEL_MARK),
                    Comments = ResolveStringParam(elem, BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS),

                    // Bounding box — convert feet → mm
                    MinX = ToMm(bb.Min.X),
                    MinY = ToMm(bb.Min.Y),
                    MinZ = ToMm(bb.Min.Z),
                    MaxX = ToMm(bb.Max.X),
                    MaxY = ToMm(bb.Max.Y),
                    MaxZ = ToMm(bb.Max.Z),
                };

                // Location data
                ExtractLocation(elem, data);

                // MEP-specific
                if (elementType == "MEP")
                {
                    ExtractSystemData(elem, data);
                    ExtractMepSizing(elem, category, data);
                }

                // Architecture-specific
                if (elementType == "Architecture")
                    ExtractArchData(elem, category, data);

                return data;
            }
            catch
            {
                return null;
            }
        }

        // ── Location Extraction ──────────────────────────────────────────

        private void ExtractLocation(Element elem, MepElementData data)
        {
            try
            {
                Location loc = elem.Location;

                if (loc is LocationCurve locCurve)
                {
                    // Pipes, ducts, conduits, cable trays
                    Curve curve = locCurve.Curve;
                    XYZ start = curve.GetEndPoint(0);
                    XYZ end = curve.GetEndPoint(1);
                    XYZ dir = (end - start).Normalize();

                    data.HasLocationCurve = true;
                    data.StartX = ToMm(start.X);
                    data.StartY = ToMm(start.Y);
                    data.StartZ = ToMm(start.Z);
                    data.EndX = ToMm(end.X);
                    data.EndY = ToMm(end.Y);
                    data.EndZ = ToMm(end.Z);
                    data.LengthMm = ToMm(curve.Length);
                    data.DirectionX = Math.Round(dir.X, 4);
                    data.DirectionY = Math.Round(dir.Y, 4);
                    data.DirectionZ = Math.Round(dir.Z, 4);
                }
                else if (loc is LocationPoint locPoint)
                {
                    // Equipment, sprinklers, fixtures
                    XYZ pt = locPoint.Point;

                    data.HasLocationPoint = true;
                    data.PointX = ToMm(pt.X);
                    data.PointY = ToMm(pt.Y);
                    data.PointZ = ToMm(pt.Z);
                    data.RotationDegrees = Math.Round(
                        locPoint.Rotation * (180.0 / Math.PI), 2);
                }
            }
            catch { }
        }

        // ── MEP System Extraction ────────────────────────────────────────

        private void ExtractSystemData(Element elem, MepElementData data)
        {
            try
            {
                // System classification (Supply Air, Domestic Hot Water, etc.)
                Parameter sysClassParam = elem.get_Parameter(
                    BuiltInParameter.RBS_SYSTEM_CLASSIFICATION_PARAM);
                if (sysClassParam != null)
                    data.SystemClassification = sysClassParam.AsString() ?? string.Empty;

                // System type name
                Parameter sysTypeParam = elem.get_Parameter(
                    BuiltInParameter.RBS_PIPING_SYSTEM_TYPE_PARAM)
                    ?? elem.get_Parameter(BuiltInParameter.RBS_DUCT_SYSTEM_TYPE_PARAM);
                if (sysTypeParam != null)
                {
                    ElementId sysTypeId = sysTypeParam.AsElementId();
                    if (sysTypeId != ElementId.InvalidElementId)
                    {
                        Element sysType = _doc.GetElement(sysTypeId);
                        data.SystemType = sysType?.Name ?? string.Empty;
                    }
                }

                // System name (the actual system instance)
                Parameter sysNameParam = elem.get_Parameter(
                    BuiltInParameter.RBS_SYSTEM_NAME_PARAM);
                if (sysNameParam != null)
                    data.SystemName = sysNameParam.AsString() ?? string.Empty;
            }
            catch { }
        }

        // ── MEP Sizing Extraction ────────────────────────────────────────

        private void ExtractMepSizing(Element elem,
                                      BuiltInCategory category,
                                      MepElementData data)
        {
            try
            {
                switch (category)
                {
                    case BuiltInCategory.OST_DuctCurves:
                    case BuiltInCategory.OST_FlexDuctCurves:
                        // Try rectangular first, then round
                        data.DuctWidthMm = GetParamMm(elem, BuiltInParameter.RBS_CURVE_WIDTH_PARAM);
                        data.DuctHeightMm = GetParamMm(elem, BuiltInParameter.RBS_CURVE_HEIGHT_PARAM);
                        data.DiameterMm = GetParamMm(elem, BuiltInParameter.RBS_CURVE_DIAMETER_PARAM);
                        data.InsulationMm = GetParamMm(elem, BuiltInParameter.RBS_INSULATION_THICKNESS);
                        data.LiningMm = GetParamMm(elem, BuiltInParameter.RBS_LINING_THICKNESS);
                        break;

                    case BuiltInCategory.OST_PipeCurves:
                    case BuiltInCategory.OST_FlexPipeCurves:
                        data.DiameterMm = GetParamMm(elem, BuiltInParameter.RBS_PIPE_OUTER_DIAMETER);
                        data.InsulationMm = GetParamMm(elem, BuiltInParameter.RBS_INSULATION_THICKNESS);
                        break;

                    case BuiltInCategory.OST_Conduit:
                        data.DiameterMm = GetParamMm(elem, BuiltInParameter.RBS_CONDUIT_OUTER_DIAM_PARAM);
                        break;

                    case BuiltInCategory.OST_CableTray:
                        data.DuctWidthMm = GetParamMm(elem, BuiltInParameter.RBS_CABLETRAY_WIDTH_PARAM);
                        data.DuctHeightMm = GetParamMm(elem, BuiltInParameter.RBS_CABLETRAY_HEIGHT_PARAM);
                        break;
                }
            }
            catch { }
        }

        // ── Architecture Extraction ──────────────────────────────────────

        // ── Architecture Extraction ──────────────────────────────────────

        private void ExtractArchData(Element elem, BuiltInCategory category, MepElementData data)
        {
            try
            {
                if (category == BuiltInCategory.OST_Walls)
                {
                    data.WallThicknessMm = GetParamMm(elem, BuiltInParameter.WALL_ATTR_WIDTH_PARAM);

                    // FIX: Replaced deleted BuiltInParameter with LookupParameter
                    Parameter structParam = elem.LookupParameter("Structural Usage");
                    if (structParam != null)
                        data.StructuralUsage = structParam.AsValueString() ?? structParam.AsString() ?? string.Empty;
                }

                if (category == BuiltInCategory.OST_StructuralFraming ||
                    category == BuiltInCategory.OST_StructuralColumns)
                {
                    // FIX: Replaced deleted BuiltInParameter with LookupParameter
                    Parameter structParam = elem.LookupParameter("Structural Usage");
                    if (structParam != null)
                        data.StructuralUsage = structParam.AsValueString() ?? structParam.AsString() ?? string.Empty;
                }
            }
            catch { }
        }

        // ── Resolve Helpers ──────────────────────────────────────────────

        private string ResolveFamilyName(Element elem)
        {
            try
            {
                if (elem is FamilyInstance fi)
                    return fi.Symbol?.FamilyName ?? string.Empty;
                return elem.GetType().Name;
            }
            catch { return string.Empty; }
        }

        private string ResolveTypeName(Element elem)
        {
            try
            {
                ElementId typeId = elem.GetTypeId();
                if (typeId != ElementId.InvalidElementId)
                    return _doc.GetElement(typeId)?.Name ?? string.Empty;
            }
            catch { }
            return string.Empty;
        }

        private string ResolveLevelName(Element elem)
        {
            try
            {
                Parameter p = elem.get_Parameter(BuiltInParameter.RBS_START_LEVEL_PARAM)
                           ?? elem.get_Parameter(BuiltInParameter.FAMILY_LEVEL_PARAM)
                           ?? elem.get_Parameter(BuiltInParameter.SCHEDULE_LEVEL_PARAM);

                if (p != null && p.AsElementId() != ElementId.InvalidElementId)
                    return _doc.GetElement(p.AsElementId())?.Name ?? "Unknown Level";
            }
            catch { }
            return "Unknown Level";
        }

        private string ResolveWorksetName(Element elem)
        {
            try
            {
                if (!_doc.IsWorkshared) return "Not Workshared";
                WorksetId wsId = elem.WorksetId;
                Workset ws = _doc.GetWorksetTable().GetWorkset(wsId);
                return ws?.Name ?? string.Empty;
            }
            catch { return string.Empty; }
        }

        private string ResolveStringParam(Element elem, BuiltInParameter param)
        {
            try
            {
                return elem.get_Parameter(param)?.AsString() ?? string.Empty;
            }
            catch { return string.Empty; }
        }

        // ── Unit Conversion ──────────────────────────────────────────────

        /// <summary>
        /// Converts Revit internal feet to millimeters.
        /// Returns null if the parameter was not found or has no value.
        /// </summary>
        private double? GetParamMm(Element elem, BuiltInParameter param)
        {
            try
            {
                Parameter p = elem.get_Parameter(param);
                if (p == null || p.StorageType != StorageType.Double)
                    return null;
                return Math.Round(p.AsDouble() * FeetToMm, 2);
            }
            catch { return null; }
        }

        private static double ToMm(double feet)
            => Math.Round(feet * FeetToMm, 2);
    }
}