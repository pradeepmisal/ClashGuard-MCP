using System.Collections.Generic;
using System.Text;
using ClashGuardRevit.Models;

namespace ClashGuardRevit.Services
{
    /// <summary>
    /// Converts MepCollectionResult into MCP-compatible JSON payload.
    /// No external libraries needed — pure string building.
    /// </summary>
    public static class McpPayloadSerializer
    {
        /// <summary>
        /// Serialize a full collection into MCP JSON format.
        /// </summary>
        public static string Serialize(MepCollectionResult collection)
        {
            var sb = new StringBuilder();

            sb.AppendLine("{");
            sb.AppendLine($"  \"model_name\": \"{Escape(collection.ModelName)}\",");
            sb.AppendLine($"  \"model_path\": \"{Escape(collection.ModelPath)}\",");
            sb.AppendLine($"  \"total_count\": {collection.TotalCount},");
            sb.AppendLine($"  \"mep_count\": {collection.MepCount},");
            sb.AppendLine($"  \"arch_count\": {collection.ArchCount},");
            sb.AppendLine($"  \"elements\": [");

            for (int i = 0; i < collection.Elements.Count; i++)
            {
                bool isLast = i == collection.Elements.Count - 1;
                sb.Append(SerializeElement(collection.Elements[i]));
                sb.AppendLine(isLast ? "" : ",");
            }

            sb.AppendLine("  ]");
            sb.AppendLine("}");

            return sb.ToString();
        }

        /// <summary>
        /// Serialize single element to MCP format.
        /// </summary>
        public static string SerializeElement(MepElementData e)
        {
            var sb = new StringBuilder();

            sb.AppendLine("    {");
            sb.AppendLine($"      \"id\": \"{e.ElementId}\",");
            sb.AppendLine($"      \"category\": \"{Escape(e.Category)}\",");
            sb.AppendLine($"      \"element_type\": \"{Escape(e.ElementType)}\",");
            sb.AppendLine($"      \"family\": \"{Escape(e.FamilyName)}\",");
            sb.AppendLine($"      \"type_name\": \"{Escape(e.TypeName)}\",");
            sb.AppendLine($"      \"level\": \"{Escape(e.LevelName)}\",");
            sb.AppendLine($"      \"workset\": \"{Escape(e.WorksetName)}\",");
            sb.AppendLine($"      \"system\": \"{Escape(e.SystemClassification)}\",");
            sb.AppendLine($"      \"system_name\": \"{Escape(e.SystemName)}\",");

            // Bounding box — array format
            sb.AppendLine($"      \"bbox\": {{");
            sb.AppendLine($"        \"min\": [{e.MinX}, {e.MinY}, {e.MinZ}],");
            sb.AppendLine($"        \"max\": [{e.MaxX}, {e.MaxY}, {e.MaxZ}]");
            sb.AppendLine($"      }},");

            // Dimensions
            sb.AppendLine($"      \"dimensions\": {{");
            sb.AppendLine($"        \"width\": {e.Width:F2},");
            sb.AppendLine($"        \"depth\": {e.Depth:F2},");
            sb.AppendLine($"        \"height\": {e.Height:F2}");
            sb.AppendLine($"      }},");

            // Location
            sb.AppendLine($"      \"location\": {{");
            sb.AppendLine($"        \"has_curve\": {(e.HasLocationCurve ? "true" : "false")},");
            sb.AppendLine($"        \"has_point\": {(e.HasLocationPoint ? "true" : "false")},");

            if (e.HasLocationCurve)
            {
                sb.AppendLine($"        \"start\": [{e.StartX}, {e.StartY}, {e.StartZ}],");
                sb.AppendLine($"        \"end\": [{e.EndX}, {e.EndY}, {e.EndZ}],");
                sb.AppendLine($"        \"length_mm\": {e.LengthMm},");
                sb.AppendLine($"        \"direction\": [{e.DirectionX}, {e.DirectionY}, {e.DirectionZ}]");
            }
            else if (e.HasLocationPoint)
            {
                sb.AppendLine($"        \"point\": [{e.PointX}, {e.PointY}, {e.PointZ}],");
                sb.AppendLine($"        \"rotation_degrees\": {e.RotationDegrees}");
            }
            else
            {
                sb.AppendLine($"        \"point\": null");
            }

            sb.AppendLine($"      }},");

            // MEP sizing — only include if values exist
            sb.AppendLine($"      \"sizing\": {{");
            sb.AppendLine($"        \"diameter_mm\": {NullableDouble(e.DiameterMm)},");
            sb.AppendLine($"        \"width_mm\": {NullableDouble(e.DuctWidthMm)},");
            sb.AppendLine($"        \"height_mm\": {NullableDouble(e.DuctHeightMm)},");
            sb.AppendLine($"        \"insulation_mm\": {NullableDouble(e.InsulationMm)}");
            sb.AppendLine($"      }}");

            sb.Append("    }");

            return sb.ToString();
        }

        // ─────────────────────────────────────────────────────────────────

        private static string NullableDouble(double? val)
            => val.HasValue ? val.Value.ToString("F2") : "null";

        private static string Escape(string val)
            => (val ?? string.Empty)
                .Replace("\\", "\\\\")
                .Replace("\"", "\\\"");
    }
}