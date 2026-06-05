using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace ClashGuardRevit.Services
{
    /// <summary>
    /// Handles REST API communication with the ClashGuard MCP backend.
    /// </summary>
    public class ApiClient
    {
        private readonly string _baseUrl;

        // We use a static HttpClient to prevent socket exhaustion
        private static readonly HttpClient _httpClient = new HttpClient
        {
            Timeout = TimeSpan.FromSeconds(30)
        };

        public ApiClient(string baseUrl)
        {
            if (string.IsNullOrWhiteSpace(baseUrl))
                throw new ArgumentException("Base URL cannot be empty.", nameof(baseUrl));

            _baseUrl = baseUrl.TrimEnd('/');
        }

        /// <summary>
        /// POST the raw JSON string to the backend endpoint.
        /// </summary>
        public async Task<ApiResponse> SendCollectionAsync(string jsonPayload)
        {
            try
            {
                // 1. Package the JSON as an HTTP content payload
                StringContent content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

                // 2. Define your exact MCP server endpoint here
                string endpoint = $"{_baseUrl}/api/clash/collect";

                // 3. Fire the POST request to the server
                HttpResponseMessage response = await _httpClient.PostAsync(endpoint, content);

                // 4. Check the server's response
                if (response.IsSuccessStatusCode)
                {
                    string responseBody = await response.Content.ReadAsStringAsync();
                    return new ApiResponse
                    {
                        Success = true,
                        Message = "Successfully sent to MCP Server.",
                        ResponseBody = responseBody
                    };
                }
                else
                {
                    return new ApiResponse
                    {
                        Success = false,
                        Message = $"Server error: {response.StatusCode} - {response.ReasonPhrase}"
                    };
                }
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Network error: {ex.Message}"
                };
            }
        }
    }

    /// <summary>
    /// A simple wrapper so our Revit UI knows if the API call succeeded or failed.
    /// </summary>
    public class ApiResponse
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public string ResponseBody { get; set; } = string.Empty;
    }
}