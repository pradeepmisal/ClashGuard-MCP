using System.Collections.Generic;

namespace ClashGuardRevit.Models
{
    /// <summary>
    /// Unified serializable element — covers both MEP and Architecture.
    /// All units are millimeters after conversion from Revit internal feet.
    /// </summary>
    public class MepElementData
    {
        // ── Identity ────────────────────────────────────────────────────
        public long ElementId { get; set; }
        public string Category { get; set; } = string.Empty;
        public string ElementType { get; set; } = string.Empty;  // MEP or Architecture
        public string FamilyName { get; set; } = string.Empty;
        public string TypeName { get; set; } = string.Empty;
        public string LevelName { get; set; } = string.Empty;
        public string WorksetName { get; set; } = string.Empty;
        public string Mark { get; set; } = string.Empty;
        public string Comments { get; set; } = string.Empty;

        // ── Bounding Box (mm) ───────────────────────────────────────────
        public double MinX { get; set; }
        public double MinY { get; set; }
        public double MinZ { get; set; }
        public double MaxX { get; set; }
        public double MaxY { get; set; }
        public double MaxZ { get; set; }

        // Derived — backend can use directly
        public double Width => MaxX - MinX;
        public double Depth => MaxY - MinY;
        public double Height => MaxZ - MinZ;

        // ── Location Curve (mm) — pipes, ducts, conduits ────────────────
        public bool HasLocationCurve { get; set; }
        public double? StartX { get; set; }
        public double? StartY { get; set; }
        public double? StartZ { get; set; }
        public double? EndX { get; set; }
        public double? EndY { get; set; }
        public double? EndZ { get; set; }
        public double? LengthMm { get; set; }

        // Direction unit vector — for orientation-aware clash checks
        public double? DirectionX { get; set; }
        public double? DirectionY { get; set; }
        public double? DirectionZ { get; set; }

        // ── Location Point (mm) — equipment, sprinklers, fixtures ───────
        public bool HasLocationPoint { get; set; }
        public double? PointX { get; set; }
        public double? PointY { get; set; }
        public double? PointZ { get; set; }
        public double? RotationDegrees { get; set; }

        // ── MEP System Data ─────────────────────────────────────────────
        public string SystemType { get; set; } = string.Empty;
        public string SystemName { get; set; } = string.Empty;
        public string SystemClassification { get; set; } = string.Empty;

        // ── MEP Sizing Parameters (mm) ──────────────────────────────────
        public double? DuctWidthMm { get; set; }   // Rectangular duct
        public double? DuctHeightMm { get; set; }
        public double? DiameterMm { get; set; }   // Round duct / pipe / conduit
        public double? InsulationMm { get; set; }   // Pipe/duct insulation thickness
        public double? LiningMm { get; set; }   // Duct lining thickness

        // ── Architecture-specific ────────────────────────────────────────
        public double? WallThicknessMm { get; set; }
        public string StructuralUsage { get; set; } = string.Empty;  // Bearing / NonBearing
    }

    /// <summary>
    /// Top-level payload sent to backend per collection run.
    /// </summary>
    public class MepCollectionResult
    {
        public string ModelName { get; set; } = string.Empty;
        public string ModelPath { get; set; } = string.Empty;
        public int TotalCount { get; set; }
        public int MepCount { get; set; }
        public int ArchCount { get; set; }
        public List<MepElementData> Elements { get; set; } = new List<MepElementData>();
    }
}