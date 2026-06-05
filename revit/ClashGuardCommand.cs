using System;
using System.Text;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using ClashGuardRevit.Services;
using ClashGuardRevit.Models;

namespace ClashGuardRevit
{
    [Transaction(TransactionMode.Manual)]
    public class ClashGuardCommand : IExternalCommand
    {
        private const string BackendUrl = "http://localhost:5000";

        public Result Execute(ExternalCommandData commandData,
                              ref string message,
                              ElementSet elements)
        {
            UIDocument uidoc = commandData.Application.ActiveUIDocument;
            Document doc = uidoc.Document;

            try
            {
                // Step 1: Collect elements
                var linkedCollector = new LinkedModelCollector(doc);
                MepCollectionResult collection = linkedCollector.CollectIncludingLinks();

                // Step 1.5: Export to JSON for backend team review
                string json = McpPayloadSerializer.Serialize(collection);
                string outputPath = System.IO.Path.Combine(
                    System.Environment.GetFolderPath(System.Environment.SpecialFolder.Desktop),
                    "clashguard_payloads.json"
                );
                System.IO.File.WriteAllText(outputPath, json);

                TaskDialog.Show("ClashGuard — JSON Exported",
                    $"MCP payload saved to Desktop:\n\n" +
                    $"clashguard_payloads.json\n\n" +
                    $"Elements: {collection.TotalCount}\n" +
                    $"MEP: {collection.MepCount}\n" +
                    $"Architecture: {collection.ArchCount}\n\n" +
                    $"Running local clash detection...");

                // Step 2: Run local AABB clash detection (deterministic)
                var mockDetector = new Services.MockClashDetector();
                var clashResult  = mockDetector.DetectClashes(collection);

                // Step 3: Visualize results inside Revit
                var visualizer = new Services.ClashVisualizer(uidoc);
                visualizer.ShowClashResults(clashResult);


                return Result.Succeeded;
            }
            catch (Exception ex)
            {
                message = ex.Message;
                TaskDialog.Show("ClashGuard — Error", ex.Message);
                return Result.Failed;
            }
        }
    }
}