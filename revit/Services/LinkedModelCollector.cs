using System;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using ClashGuardRevit.Models;

namespace ClashGuardRevit.Services
{
    /// <summary>
    /// Wraps the basic collector to handle linked RVT documents.
    /// Traverses the RevitLinkInstance elements and collects from each linked doc.
    /// </summary>
    public class LinkedModelCollector
    {
        private readonly Document _hostDoc;
        private readonly Collectors.MepElementCollector _baseCollector;

        public LinkedModelCollector(Document hostDoc)
        {
            _hostDoc = hostDoc ?? throw new ArgumentNullException(nameof(hostDoc));
            _baseCollector = new Collectors.MepElementCollector(hostDoc);
        }

        /// <summary>
        /// Collect from host doc + all accessible linked models.
        /// Returns a combined result with source tracking.
        /// </summary>
        public MepCollectionResult CollectIncludingLinks()
        {
            // Start with host document collection
            MepCollectionResult hostResult = _baseCollector.Collect();
            hostResult.ModelPath = _hostDoc.PathName;

            // Track all linked documents
            var linkedResults = new List<MepCollectionResult>();

            // Find all RevitLinkInstance elements in the host
            var linkCollector = new FilteredElementCollector(_hostDoc)
                .OfClass(typeof(RevitLinkInstance));

            foreach (RevitLinkInstance linkInstance in linkCollector)
            {
                MepCollectionResult linkedResult = CollectFromLink(linkInstance);
                if (linkedResult != null && linkedResult.TotalCount > 0)
                    linkedResults.Add(linkedResult);
            }

            // Merge all results
            return MergeResults(hostResult, linkedResults);
        }

        // ─────────────────────────────────────────────────────────────────

        private MepCollectionResult CollectFromLink(RevitLinkInstance linkInstance)
        {
            try
            {
                // Skip unloaded links — check if the link document is actually accessible
                Document linkedDoc = null;
                try
                {
                    linkedDoc = linkInstance.GetLinkDocument();
                }
                catch
                {
                    // Link is unloaded or broken — skip it
                    return null;
                }

                if (linkedDoc == null)
                    return null;

                var linkedCollector = new Collectors.MepElementCollector(linkedDoc);
                MepCollectionResult result = linkedCollector.Collect();

                // Tag with link instance info
                result.ModelPath = linkedDoc.PathName;
                foreach (var elem in result.Elements)
                    elem.Comments = $"[Link: {linkInstance.Name}] {elem.Comments}";

                return result;
            }
            catch
            {
                // Individual link failures don't crash the whole operation
                return null;
            }
        }

        private MepCollectionResult MergeResults(MepCollectionResult host,
                                                  List<MepCollectionResult> linked)
        {
            var merged = new MepCollectionResult
            {
                ModelName = host.ModelName,
                ModelPath = host.ModelPath
            };

            // Add host elements
            merged.Elements.AddRange(host.Elements);

            // Add linked elements
            foreach (var linkedResult in linked)
                merged.Elements.AddRange(linkedResult.Elements);

            // Recalculate counts
            merged.TotalCount = merged.Elements.Count;
            merged.MepCount = merged.Elements.FindAll(e => e.ElementType == "MEP").Count;
            merged.ArchCount = merged.Elements.FindAll(e => e.ElementType == "Architecture").Count;

            return merged;
        }
    }
}