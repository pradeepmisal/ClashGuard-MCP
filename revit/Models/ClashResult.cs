using System.Collections.Generic;

namespace ClashGuardRevit.Models
{
    /// <summary>
    /// Represents a single clash between two elements.
    /// Backend will return a list of these after analyzing the model.
    /// </summary>
    public class Clash
    {
        public long ElementId1 { get; set; }
        public long ElementId2 { get; set; }
        public string Element1Name { get; set; } = string.Empty;
        public string Element2Name { get; set; } = string.Empty;
        public string ClashType { get; set; } = string.Empty;  // e.g., "Pipe-Wall", "Duct-Beam"
        public double OverlapVolume { get; set; }  // Volume of intersection in mm³
        public string Severity { get; set; } = "Medium";  // Critical, High, Medium, Low
        public string Description { get; set; } = string.Empty;
    }

    /// <summary>
    /// Complete clash analysis results from backend.
    /// </summary>
    public class ClashAnalysisResult
    {
        public string ModelName { get; set; } = string.Empty;
        public int TotalElementsScanned { get; set; }
        public int TotalClashesFound { get; set; }
        public int CriticalClashes { get; set; }
        public int HighClashes { get; set; }
        public int MediumClashes { get; set; }
        public int LowClashes { get; set; }
        public List<Clash> Clashes { get; set; } = new List<Clash>();
    }
}