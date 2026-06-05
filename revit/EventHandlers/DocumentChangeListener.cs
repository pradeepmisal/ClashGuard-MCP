using System;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Events;

namespace ClashGuardRevit.EventHandlers
{
    /// <summary>
    /// Subscribes to DocumentChanged events to detect model modifications.
    /// Triggers a rescan when significant changes are detected.
    /// </summary>
    public class DocumentChangeListener : IDisposable
    {
        private readonly Application _app;
        public event EventHandler<DocumentChangedEventArgs> OnModelChanged;

        public DocumentChangeListener(Application app)
        {
            _app = app ?? throw new ArgumentNullException(nameof(app));
        }

        /// <summary>
        /// Start listening for changes on all documents.
        /// </summary>
        public void Subscribe()
        {
            _app.DocumentChanged += App_DocumentChanged;
        }

        /// <summary>
        /// Stop listening.
        /// </summary>
        public void Unsubscribe()
        {
            _app.DocumentChanged -= App_DocumentChanged;
        }

        // ─────────────────────────────────────────────────────────────────

        private void App_DocumentChanged(object sender, DocumentChangedEventArgs e)
        {
            Document doc = e.GetDocument();

            // Skip if no relevant changes
            if (!HasRelevantChanges(e))
                return;

            // Raise event for external handlers (command, UI, etc.)
            OnModelChanged?.Invoke(this, e);
        }

        /// <summary>
        /// Determines if the change is worth rescanning.
        /// Ignores cosmetic/view-only changes.
        /// </summary>
        private bool HasRelevantChanges(DocumentChangedEventArgs e)
        {
            // If elements were added, deleted, or modified in geometry/properties
            if (e.GetAddedElementIds().Count > 0)
                return true;

            if (e.GetDeletedElementIds().Count > 0)
                return true;

            // Modified element IDs — check if they're MEP/Architecture
            if (e.GetModifiedElementIds().Count > 0)
            {
                foreach (ElementId elemId in e.GetModifiedElementIds())
                {
                    if (IsRelevantCategory(e.GetDocument(), elemId))
                        return true;
                }
            }

            return false;
        }

        private bool IsRelevantCategory(Document doc, ElementId elemId)
        {
            try
            {
                Element elem = doc.GetElement(elemId);
                if (elem == null)
                    return false;

                // Only care about actual building elements, not views, sheets, etc.
                BuiltInCategory cat = (BuiltInCategory)elem.Category.Id.Value;

                return IsMepCategory(cat) || IsArchCategory(cat);
            }
            catch
            {
                return false;
            }
        }

        private static bool IsMepCategory(BuiltInCategory cat)
        {
            return cat == BuiltInCategory.OST_DuctCurves
                || cat == BuiltInCategory.OST_PipeCurves
                || cat == BuiltInCategory.OST_Conduit
                || cat == BuiltInCategory.OST_CableTray
                || cat == BuiltInCategory.OST_MechanicalEquipment
                || cat == BuiltInCategory.OST_ElectricalEquipment
                || cat == BuiltInCategory.OST_PlumbingFixtures
                || cat == BuiltInCategory.OST_FireProtection;
        }

        private static bool IsArchCategory(BuiltInCategory cat)
        {
            return cat == BuiltInCategory.OST_Walls
                || cat == BuiltInCategory.OST_Doors
                || cat == BuiltInCategory.OST_Windows
                || cat == BuiltInCategory.OST_Floors
                || cat == BuiltInCategory.OST_Ceilings
                || cat == BuiltInCategory.OST_StructuralFraming
                || cat == BuiltInCategory.OST_StructuralColumns
                || cat == BuiltInCategory.OST_Roofs;
        }

        public void Dispose()
        {
            Unsubscribe();
            _app?.Dispose();
        }
    }
}