using System;
using System.Collections.Generic;
using System.Linq;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using ClashGuardRevit.Models;

namespace ClashGuardRevit.Services
{
    /// <summary>
    /// Visualizes clash results in Revit.
    /// Selects clashing elements, highlights them, and provides zoom-to-clash.
    /// </summary>
    public class ClashVisualizer
    {
        private readonly UIDocument _uidoc;
        private readonly Document _doc;

        public ClashVisualizer(UIDocument uidoc)
        {
            _uidoc = uidoc ?? throw new ArgumentNullException(nameof(uidoc));
            _doc = uidoc.Document;
        }

        /// <summary>
        /// Displays clash results and allows user to navigate to clashes.
        /// </summary>
        public void ShowClashResults(ClashAnalysisResult clashResult)
        {
            if (clashResult.TotalClashesFound == 0)
            {
                TaskDialog.Show("ClashGuard — Results",
                    "✅ No clashes detected!\n\n" +
                    $"Scanned {clashResult.TotalElementsScanned} elements.");
                return;
            }

            // Show summary
            string summary = BuildSummary(clashResult);
            TaskDialog td = new TaskDialog("ClashGuard — Clash Results");
            td.MainInstruction = $"Found {clashResult.TotalClashesFound} clashes";
            td.MainContent = summary;
            td.AddCommandLink(TaskDialogCommandLinkId.CommandLink1, "View All Clashes");
            td.AddCommandLink(TaskDialogCommandLinkId.CommandLink2, "View Critical Only");
            td.AddCommandLink(TaskDialogCommandLinkId.CommandLink3, "Close");

            TaskDialogResult result = td.Show();

            switch (result)
            {
                case TaskDialogResult.CommandLink1:
                    DisplayClashes(clashResult.Clashes, null);
                    break;

                case TaskDialogResult.CommandLink2:
                    var criticalOnly = clashResult.Clashes
                        .Where(c => c.Severity == "Critical")
                        .ToList();
                    DisplayClashes(criticalOnly, "Critical");
                    break;

                default:
                    break;
            }
        }

        // ─────────────────────────────────────────────────────────────────

        private void DisplayClashes(List<Clash> clashes, string? filterSeverity)
        {
            if (clashes.Count == 0)
            {
                TaskDialog.Show("ClashGuard", "No clashes to display.");
                return;
            }

            var elementIds = new List<ElementId>();

            foreach (var clash in clashes)
            {
                ElementId id1 = new ElementId(clash.ElementId1);
                ElementId id2 = new ElementId(clash.ElementId2);

                if (_doc.GetElement(id1) != null)
                    elementIds.Add(id1);

                if (_doc.GetElement(id2) != null)
                    elementIds.Add(id2);
            }

            if (elementIds.Count == 0)
            {
                TaskDialog.Show("ClashGuard", "Clashing elements not found in model.\n" +
                    "(They may be in linked documents)");
                return;
            }

            // Select clashing elements
            _uidoc.Selection.SetElementIds(elementIds);

            // Zoom to first clash
            if (clashes.Count > 0)
            {
                ZoomToClash(clashes[0]);
            }

            // Show detailed list
            string details = BuildClashDetails(clashes, filterSeverity);
            TaskDialog.Show("ClashGuard — Clash Details", details);
        }

        private void ZoomToClash(Clash clash)
        {
            try
            {
                Element elem1 = _doc.GetElement(new ElementId(clash.ElementId1));
                Element elem2 = _doc.GetElement(new ElementId(clash.ElementId2));

                if (elem1 == null || elem2 == null)
                    return;

                // Get bounding boxes
                BoundingBoxXYZ bb1 = elem1.get_BoundingBox(null);
                BoundingBoxXYZ bb2 = elem2.get_BoundingBox(null);

                if (bb1 == null || bb2 == null)
                    return;

                // Compute combined bounding box
                XYZ min = new XYZ(
                    Math.Min(bb1.Min.X, bb2.Min.X),
                    Math.Min(bb1.Min.Y, bb2.Min.Y),
                    Math.Min(bb1.Min.Z, bb2.Min.Z)
                );

                XYZ max = new XYZ(
                    Math.Max(bb1.Max.X, bb2.Max.X),
                    Math.Max(bb1.Max.Y, bb2.Max.Y),
                    Math.Max(bb1.Max.Z, bb2.Max.Z)
                );

                BoundingBoxXYZ zoomBox = new BoundingBoxXYZ { Min = min, Max = max };

                // Set section box to zoom region
                View activeView = _uidoc.ActiveView;
                if (activeView.ViewType == ViewType.ThreeD)
                {
                    View3D view3d = (View3D)activeView;
                    if (!view3d.IsLocked)
                    {
                        view3d.SetSectionBox(zoomBox);
                    }
                }
            }
            catch
            {
                // Zoom failed — not critical, continue
            }
        }

        private string BuildSummary(ClashAnalysisResult result)
        {
            var sb = new System.Text.StringBuilder();
            sb.AppendLine($"Model: {result.ModelName}");
            sb.AppendLine($"Scanned: {result.TotalElementsScanned} elements");
            sb.AppendLine();
            sb.AppendLine($"Total Clashes: {result.TotalClashesFound}");
            sb.AppendLine($"  🔴 Critical: {result.CriticalClashes}");
            sb.AppendLine($"  🟠 High:     {result.HighClashes}");
            sb.AppendLine($"  🟡 Medium:   {result.MediumClashes}");
            sb.AppendLine($"  🟢 Low:      {result.LowClashes}");

            return sb.ToString();
        }

        private string BuildClashDetails(List<Clash> clashes, string filterSeverity)
        {
            var sb = new System.Text.StringBuilder();

            var displayed = filterSeverity == null
                ? clashes
                : clashes.Where(c => c.Severity == filterSeverity).ToList();

            foreach (var clash in displayed.Take(10))  // Show first 10
            {
                sb.AppendLine($"[{clash.Severity}] {clash.ClashType}");
                sb.AppendLine($"  {clash.Element1Name}");
                sb.AppendLine($"  vs");
                sb.AppendLine($"  {clash.Element2Name}");
                sb.AppendLine($"  {clash.Description}");
                sb.AppendLine();
            }

            if (displayed.Count > 10)
                sb.AppendLine($"... and {displayed.Count - 10} more clashes");

            return sb.ToString();
        }
    }
}