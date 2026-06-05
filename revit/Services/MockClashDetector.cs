using System;
using System.Collections.Generic;
using System.Linq;
using ClashGuardRevit.Models;

namespace ClashGuardRevit.Services
{
    /// <summary>
    /// Mock clash detector — simulates backend clash analysis.
    /// When real backend is ready, replace with ApiClient.SendCollectionAsync().
    /// </summary>
    public class MockClashDetector
    {
        /// <summary>
        /// Analyzes collected elements and returns simulated clash results.
        /// Uses spatial bounding box overlap to detect potential clashes.
        /// </summary>
        public ClashAnalysisResult DetectClashes(MepCollectionResult collection)
        {
            var result = new ClashAnalysisResult
            {
                ModelName = collection.ModelName,
                TotalElementsScanned = collection.TotalCount
            };

            // Find spatial overlaps
            var mepElements = collection.Elements
                .Where(e => e.ElementType == "MEP")
                .ToList();

            var archElements = collection.Elements
                .Where(e => e.ElementType == "Architecture")
                .ToList();

            foreach (var mep in mepElements)
            {
                foreach (var arch in archElements)
                {
                    if (BoundingBoxesOverlap(mep, arch))
                    {
                        var clash = new Clash
                        {
                            ElementId1 = mep.ElementId,
                            ElementId2 = arch.ElementId,
                            Element1Name = $"{mep.Category} (ID: {mep.ElementId})",
                            Element2Name = $"{arch.Category} (ID: {arch.ElementId})",
                            ClashType = $"{mep.Category}-{arch.Category}",
                            Severity = DetermineSeverity(mep, arch),
                            Description = $"{mep.Category} overlaps {arch.Category} on {arch.LevelName}"
                        };

                        result.Clashes.Add(clash);
                    }
                }
            }

            // ───────────────────────────────────────────────────────────────
            // FOR TESTING: Inject fake clashes if none found
            // Remove this block after testing ↓
            // ───────────────────────────────────────────────────────────────

            if (result.Clashes.Count == 0 && mepElements.Count > 0 && archElements.Count > 0)
            {
                // Create a fake clash for testing visualization
                result.Clashes.Add(new Clash
                {
                    ElementId1 = mepElements[0].ElementId,
                    ElementId2 = archElements[0].ElementId,
                    Element1Name = $"TEST: {mepElements[0].Category} (ID: {mepElements[0].ElementId})",
                    Element2Name = $"TEST: {archElements[0].Category} (ID: {archElements[0].ElementId})",
                    ClashType = $"{mepElements[0].Category}-{archElements[0].Category}",
                    Severity = "Critical",
                    Description = "[TEST CLASH] This is a fake clash injected for testing visualization"
                });

                // Add a few more test clashes with different severities
                if (mepElements.Count > 1 && archElements.Count > 1)
                {
                    result.Clashes.Add(new Clash
                    {
                        ElementId1 = mepElements[1].ElementId,
                        ElementId2 = archElements[1].ElementId,
                        Element1Name = $"TEST: {mepElements[1].Category}",
                        Element2Name = $"TEST: {archElements[1].Category}",
                        ClashType = "TEST",
                        Severity = "High",
                        Description = "[TEST CLASH] High severity test"
                    });

                    result.Clashes.Add(new Clash
                    {
                        ElementId1 = mepElements[0].ElementId,
                        ElementId2 = archElements[1].ElementId,
                        Element1Name = $"TEST: {mepElements[0].Category}",
                        Element2Name = $"TEST: {archElements[1].Category}",
                        ClashType = "TEST",
                        Severity = "Medium",
                        Description = "[TEST CLASH] Medium severity test"
                    });
                }
            }

            // ───────────────────────────────────────────────────────────────
            // END TEST SECTION ↑ — Delete this after you verify visualization works
            // ───────────────────────────────────────────────────────────────

            // Tally severity counts
            result.TotalClashesFound = result.Clashes.Count;
            result.CriticalClashes = result.Clashes.Count(c => c.Severity == "Critical");
            result.HighClashes = result.Clashes.Count(c => c.Severity == "High");
            result.MediumClashes = result.Clashes.Count(c => c.Severity == "Medium");
            result.LowClashes = result.Clashes.Count(c => c.Severity == "Low");

            return result;
        }

        // ─────────────────────────────────────────────────────────────────


        private bool BoundingBoxesOverlap(MepElementData elem1, MepElementData elem2)
        {
            // Two 3D boxes overlap if they overlap on all three axes
            bool xOverlap = elem1.MinX < elem2.MaxX && elem1.MaxX > elem2.MinX;
            bool yOverlap = elem1.MinY < elem2.MaxY && elem1.MaxY > elem2.MinY;
            bool zOverlap = elem1.MinZ < elem2.MaxZ && elem1.MaxZ > elem2.MinZ;

            return xOverlap && yOverlap && zOverlap;
        }

        private string DetermineSeverity(MepElementData mep, MepElementData arch)
        {
            // Simple heuristic: if significant overlap, it's critical
            double overlapX = Math.Min(mep.MaxX, arch.MaxX) - Math.Max(mep.MinX, arch.MinX);
            double overlapY = Math.Min(mep.MaxY, arch.MaxY) - Math.Max(mep.MinY, arch.MinY);
            double overlapZ = Math.Min(mep.MaxZ, arch.MaxZ) - Math.Max(mep.MinZ, arch.MinZ);

            double overlapVolume = overlapX * overlapY * overlapZ;
            double mepVolume = mep.Width * mep.Depth * mep.Height;

            double percentOverlap = (overlapVolume / mepVolume) * 100;

            if (percentOverlap > 50) return "Critical";
            if (percentOverlap > 25) return "High";
            if (percentOverlap > 10) return "Medium";
            return "Low";
        }
    }
}

