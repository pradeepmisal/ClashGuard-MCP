using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Events;
using Autodesk.Revit.UI;

namespace ClashGuardRevit
{
    public class ClashGuardAddin : IExternalApplication
    {
        public Result OnStartup(UIControlledApplication application)
        {
            try
            {
                application.ControlledApplication.DocumentOpened += OnDocumentOpened;
                return Result.Succeeded;
            }
            catch
            {
                return Result.Failed;
            }
        }

        public Result OnShutdown(UIControlledApplication application)
        {
            try
            {
                application.ControlledApplication.DocumentOpened -= OnDocumentOpened;
                return Result.Succeeded;
            }
            catch
            {
                return Result.Failed;
            }
        }

        private void OnDocumentOpened(object sender, DocumentOpenedEventArgs e)
        {
            try
            {
                Document doc = e.Document;
                doc.Application.DocumentChanged += (s, args) =>
                {
                    try
                    {
                        if (HasRelevantChanges(args))
                        {
                            int added = args.GetAddedElementIds().Count;
                            int modified = args.GetModifiedElementIds().Count;
                            int deleted = args.GetDeletedElementIds().Count;

                            TaskDialog.Show("ClashGuard — Change Detected ✅",
                                $"Added:    {added}\n" +
                                $"Modified: {modified}\n" +
                                $"Deleted:  {deleted}");
                        }
                    }
                    catch (Exception ex)
                    {
                        TaskDialog.Show("❌ DocumentChanged Error", ex.Message);
                    }
                };

                // Confirm subscription happened
                TaskDialog.Show("✅ ClashGuard Monitoring Active",
                    $"Listening for changes on:\n{doc.Title}");
            }
            catch (Exception ex)
            {
                TaskDialog.Show("❌ OnDocumentOpened Error", ex.Message);
            }
        }

        private bool HasRelevantChanges(DocumentChangedEventArgs e)
        {
            return e.GetAddedElementIds().Count > 0
                || e.GetDeletedElementIds().Count > 0
                || e.GetModifiedElementIds().Count > 0;
        }
    }
}