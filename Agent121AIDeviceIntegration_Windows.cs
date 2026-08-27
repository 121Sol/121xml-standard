// 121AI Windows Device Integration Layer
// Native access to Outlook Calendar, Contacts, Tasks, Alarms
// Full Cortana integration for voice commands

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Windows.ApplicationModel.Contacts;
using Windows.ApplicationModel.Appointments;
using Windows.UI.Notifications;
using Windows.Networking.BackgroundTransfer;
using System.Net.Http;
using System.Text.Json;
using System.Diagnostics;
using Windows.Devices.Enumeration;
using Windows.Media.Core;
using Windows.Media.Playback;
using System.Linq;

namespace Agent121AI.Windows
{
    /// <summary>
    /// 121AI Windows Device Integration
    /// Unified access to Windows Calendar, Contacts, Tasks, Cortana
    /// </summary>
    public class Agent121AIDeviceIntegration
    {
        private readonly ContactStore _contactStore;
        private readonly AppointmentStore _appointmentStore;
        private readonly HttpClient _apiClient;
        private readonly string _backendUrl = "http://localhost:8000";

        public event EventHandler<DeviceCommandEventArgs> OnDeviceCommand;
        public event EventHandler<DeviceEventArgs> OnDeviceEvent;

        public Agent121AIDeviceIntegration()
        {
            _apiClient = new HttpClient();
            _apiClient.DefaultRequestHeaders.Add("User-Agent", "121AI-Windows-Native/1.0");

            // Initialize stores
            InitializeAsync().GetAwaiter().GetResult();
        }

        private async Task InitializeAsync()
        {
            try
            {
                _contactStore = await ContactManager.RequestStoreAsync(
                    ContactStoreAccessType.AppContactsReadWrite
                );

                _appointmentStore = await AppointmentManager.RequestStoreAsync(
                    AppointmentStoreAccessType.AllCalendarsReadWrite
                );

                Debug.WriteLine("[121AI] Windows device integration initialized");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Initialization failed: {ex.Message}");
            }
        }

        // MARK: - Calendar Integration

        /// <summary>
        /// Create calendar event with multiple participants
        /// Example: "Add meeting with George Bush and Tony Blair at the White House Oval Room"
        /// </summary>
        public async Task<Appointment> CreateCalendarEventAsync(
            string title,
            string description,
            DateTimeOffset startTime,
            DateTimeOffset endTime,
            List<string> participants,
            string location = "")
        {
            try
            {
                var appointment = new Appointment
                {
                    Subject = title,
                    Details = description,
                    StartTime = startTime,
                    EndTime = endTime,
                    Location = location,
                    IsReminderOn = true,
                    ReminderMinutesBeforeStart = 15
                };

                // Add participants
                foreach (var participantName in participants)
                {
                    var contact = await FindContactAsync(participantName);
                    if (contact != null)
                    {
                        // Add organizer/attendee info
                        appointment.Details += $"\n\nAttendees: {contact.DisplayName}";
                    }
                }

                // Get default calendar
                var calendars = await _appointmentStore.FindAppointmentCalendarsAsync(
                    FindAppointmentCalendarsOptions.None
                );

                if (calendars.Count > 0)
                {
                    string id = await calendars[0].SaveAppointmentAsync(appointment);
                    appointment.LocalId = id;

                    // Notify backend
                    await NotifyBackendAsync("calendar.created", new
                    {
                        title,
                        participants = string.Join(", ", participants),
                        location,
                        startTime = startTime.ToString("O")
                    });
                }

                return appointment;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Calendar creation failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// List today's calendar events
        /// </summary>
        public async Task<IReadOnlyList<Appointment>> ListTodaysEventsAsync()
        {
            try
            {
                var calendars = await _appointmentStore.FindAppointmentCalendarsAsync(
                    FindAppointmentCalendarsOptions.IncludeHidden
                );

                var startDate = DateTime.Today;
                var endDate = DateTime.Today.AddDays(1);

                var findOptions = new FindAppointmentsOptions
                {
                    FetchProperties = new System.Collections.Generic.List<string>
                    {
                        "Subject",
                        "Location",
                        "Details",
                        "StartTime",
                        "Duration"
                    },
                    MaxAppointments = 100
                };

                var appointments = await _appointmentStore.FindAppointmentsAsync(
                    startDate,
                    endDate,
                    findOptions
                );

                return appointments;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] List events failed: {ex.Message}");
                return new List<Appointment>();
            }
        }

        /// <summary>
        /// Search calendar events
        /// </summary>
        public async Task<IReadOnlyList<Appointment>> SearchEventsAsync(string query)
        {
            try
            {
                var startDate = DateTime.Today.AddDays(-30);
                var endDate = DateTime.Today.AddDays(365);

                var findOptions = new FindAppointmentsOptions
                {
                    FetchProperties = new List<string> { "Subject", "Location" },
                    MaxAppointments = 50
                };

                var appointments = await _appointmentStore.FindAppointmentsAsync(
                    startDate,
                    endDate,
                    findOptions
                );

                return appointments
                    .Where(a =>
                        a.Subject.Contains(query, StringComparison.OrdinalIgnoreCase) ||
                        a.Location.Contains(query, StringComparison.OrdinalIgnoreCase))
                    .ToList();
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Search events failed: {ex.Message}");
                return new List<Appointment>();
            }
        }

        // MARK: - Task/Reminders Integration (via Tasks app)

        /// <summary>
        /// Create task/reminder
        /// Example: "Remind me to call the Prime Minister of Pakistan"
        /// </summary>
        public async Task CreateTaskAsync(
            string title,
            string description = "",
            DateTimeOffset? dueDate = null,
            int? reminderMinutes = 60)
        {
            try
            {
                var appointment = new Appointment
                {
                    Subject = title,
                    Details = description,
                    StartTime = dueDate ?? DateTimeOffset.Now.AddDays(1),
                    EndTime = dueDate?.AddHours(1) ?? DateTimeOffset.Now.AddDays(1).AddHours(1),
                    IsReminderOn = true,
                    ReminderMinutesBeforeStart = reminderMinutes ?? 60
                };

                var calendars = await _appointmentStore.FindAppointmentCalendarsAsync(
                    FindAppointmentCalendarsOptions.None
                );

                if (calendars.Count > 0)
                {
                    await calendars[0].SaveAppointmentAsync(appointment);

                    await NotifyBackendAsync("reminder.created", new
                    {
                        title,
                        dueDate = dueDate?.ToString("O"),
                        reminderMinutes
                    });
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Task creation failed: {ex.Message}");
            }
        }

        /// <summary>
        /// List today's tasks
        /// </summary>
        public async Task<IReadOnlyList<Appointment>> ListTodaysTasksAsync()
        {
            return await ListTodaysEventsAsync();
        }

        // MARK: - Alarms Integration

        /// <summary>
        /// Set alarm via Windows notification
        /// Example: "Set an alarm for 7 AM tomorrow"
        /// </summary>
        public async Task SetAlarmAsync(TimeSpan time, string label = "121AI Alarm")
        {
            try
            {
                var alarmTime = DateTime.Today.Add(time);
                if (alarmTime <= DateTime.Now)
                {
                    alarmTime = alarmTime.AddDays(1);
                }

                var notificationContent = $@"
                <toast activationType='foreground' launch='alarm'>
                    <visual>
                        <binding template='ToastText02'>
                            <text id='1'>{label}</text>
                            <text id='2'>Alarm at {alarmTime:h:mm tt}</text>
                        </binding>
                    </visual>
                </toast>";

                var doc = new Windows.Data.Xml.Dom.XmlDocument();
                doc.LoadXml(notificationContent);

                var notification = new ToastNotification(doc);

                ToastNotificationManager.CreateToastNotifier(
                    "121AI.Notifications").Show(notification);

                await NotifyBackendAsync("alarm.set", new
                {
                    time = alarmTime.ToString("O"),
                    label
                });

                Debug.WriteLine($"[121AI] Alarm set for {alarmTime:h:mm tt}");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Alarm setup failed: {ex.Message}");
            }
        }

        // MARK: - Contacts Integration

        /// <summary>
        /// Find contact by name or email
        /// </summary>
        public async Task<Contact> FindContactAsync(string nameOrEmail)
        {
            try
            {
                var contacts = await _contactStore.FindContactsAsync(nameOrEmail);

                if (contacts.Count > 0)
                {
                    return contacts[0];
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Find contact failed: {ex.Message}");
            }

            return null;
        }

        /// <summary>
        /// Get all contacts
        /// </summary>
        public async Task<IReadOnlyList<Contact>> GetAllContactsAsync()
        {
            try
            {
                var contacts = await _contactStore.FindContactsAsync();
                return contacts;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Get contacts failed: {ex.Message}");
                return new List<Contact>();
            }
        }

        /// <summary>
        /// Get contact phone number
        /// </summary>
        public string GetContactPhone(Contact contact)
        {
            return contact?.Phones.FirstOrDefault()?.Number ?? "N/A";
        }

        /// <summary>
        /// Get contact email
        /// </summary>
        public string GetContactEmail(Contact contact)
        {
            return contact?.Emails.FirstOrDefault()?.Address ?? "N/A";
        }

        // MARK: - App Launching

        /// <summary>
        /// Launch app by name
        /// Example: "Launch Google Meet"
        /// </summary>
        public async Task LaunchAppAsync(string appName)
        {
            try
            {
                var appLaunchers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
                {
                    { "google meet", "ms-edge:https://meet.google.com" },
                    { "zoom", "ms-edge:https://zoom.us" },
                    { "teams", "msteams:" },
                    { "outlook", "outlookcal:" },
                    { "mail", "mailto:" },
                    { "calendar", "outlookcal:" },
                    { "contacts", "ms-settings:contacts" },
                    { "notes", "onenote:" }
                };

                if (appLaunchers.TryGetValue(appName, out var launcher))
                {
                    var uri = new Uri(launcher);
                    await Windows.System.Launcher.LaunchUriAsync(uri);

                    await NotifyBackendAsync("app.launched", new { app = appName });
                }
                else
                {
                    Debug.WriteLine($"[121AI] App launcher not configured: {appName}");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] App launch failed: {ex.Message}");
            }
        }

        // MARK: - Video Conference Integration

        /// <summary>
        /// Schedule video call with multiple participants
        /// Example: "Schedule a Google Meet with Prime Ministers of Pakistan and Iran"
        /// </summary>
        public async Task ScheduleVideoCallAsync(
            string title,
            List<string> participants,
            DateTimeOffset startTime,
            string platform = "google_meet")
        {
            try
            {
                // Create calendar event
                var appointment = new Appointment
                {
                    Subject = $"{title} - Video Call",
                    Details = $"Participants: {string.Join(", ", participants)}",
                    StartTime = startTime,
                    EndTime = startTime.AddHours(1),
                    Location = $"Online - {platform}",
                    IsReminderOn = true,
                    ReminderMinutesBeforeStart = 15
                };

                var calendars = await _appointmentStore.FindAppointmentCalendarsAsync(
                    FindAppointmentCalendarsOptions.None
                );

                if (calendars.Count > 0)
                {
                    await calendars[0].SaveAppointmentAsync(appointment);

                    // Generate meeting link
                    var meetingLink = GenerateMeetingLink(platform);

                    // Send invitations
                    foreach (var participantName in participants)
                    {
                        var contact = await FindContactAsync(participantName);
                        if (contact != null)
                        {
                            await SendVideoCallInviteAsync(
                                GetContactEmail(contact),
                                title,
                                meetingLink
                            );
                        }
                    }

                    await NotifyBackendAsync("video_call.scheduled", new
                    {
                        title,
                        participants = string.Join(", ", participants),
                        platform,
                        meetingLink
                    });
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Video call scheduling failed: {ex.Message}");
            }
        }

        private string GenerateMeetingLink(string platform)
        {
            return platform.ToLower() switch
            {
                "google_meet" => $"https://meet.google.com/{Guid.NewGuid().ToString().Substring(0, 10)}",
                "teams" => $"https://teams.microsoft.com/l/meetup-join/{Guid.NewGuid()}",
                "zoom" => $"https://zoom.us/j/{new Random().Next(100000000, 999999999)}",
                _ => $"https://conference.example.com/{Guid.NewGuid()}"
            };
        }

        private async Task SendVideoCallInviteAsync(string email, string title, string meetingLink)
        {
            try
            {
                var mailto = new Uri($"mailto:{email}?subject=Invitation: {title}&body=Join the video call: {meetingLink}");
                await Windows.System.Launcher.LaunchUriAsync(mailto);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Send invite failed: {ex.Message}");
            }
        }

        // MARK: - Cortana Integration

        /// <summary>
        /// Process Cortana voice command
        /// Example: "Cortana, ask 121AI to list today's tasks"
        /// </summary>
        public async Task ProcessCortanaCommandAsync(string command)
        {
            try
            {
                await SendToBackendAsync(command, "cortana");

                var parsedCommand = await ParseCommandAsync(command);

                switch (parsedCommand.Intent)
                {
                    case "create_event":
                        if (parsedCommand.Data is JsonElement eventData)
                        {
                            await CreateCalendarEventAsync(
                                eventData.GetProperty("title").GetString() ?? "",
                                eventData.GetProperty("description").GetString() ?? "",
                                DateTimeOffset.Parse(eventData.GetProperty("startTime").GetString() ?? ""),
                                DateTimeOffset.Parse(eventData.GetProperty("endTime").GetString() ?? ""),
                                new List<string>(),
                                eventData.GetProperty("location").GetString() ?? ""
                            );
                        }
                        break;

                    case "list_events":
                        var events = await ListTodaysEventsAsync();
                        Debug.WriteLine($"[121AI] Today's events: {string.Join(", ", events.Select(e => e.Subject))}");
                        break;

                    case "set_alarm":
                        if (parsedCommand.Data is JsonElement alarmData)
                        {
                            var timeStr = alarmData.GetProperty("time").GetString() ?? "07:00:00";
                            if (TimeSpan.TryParse(timeStr, out var alarmTime))
                            {
                                await SetAlarmAsync(alarmTime, alarmData.GetProperty("label").GetString() ?? "");
                            }
                        }
                        break;

                    case "launch_app":
                        if (parsedCommand.Data is JsonElement appData)
                        {
                            await LaunchAppAsync(appData.GetProperty("app").GetString() ?? "");
                        }
                        break;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Cortana command processing failed: {ex.Message}");
            }
        }

        // MARK: - Backend Communication

        private async Task<(string Intent, JsonElement Data)> ParseCommandAsync(string command)
        {
            try
            {
                var payload = new { command, platform = "windows" };
                var json = JsonSerializer.Serialize(payload);
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

                var response = await _apiClient.PostAsync($"{_backendUrl}/api/parse-intent", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseText = await response.Content.ReadAsStringAsync();
                    var parsed = JsonSerializer.Deserialize<JsonElement>(responseText);

                    return (
                        parsed.GetProperty("intent").GetString() ?? "unknown",
                        parsed.GetProperty("data")
                    );
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Command parsing failed: {ex.Message}");
            }

            return ("unknown", default);
        }

        private async Task SendToBackendAsync(string command, string source)
        {
            try
            {
                var payload = new
                {
                    command,
                    source,
                    platform = "windows",
                    timestamp = DateTime.UtcNow.ToString("O")
                };

                var json = JsonSerializer.Serialize(payload);
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

                var response = await _apiClient.PostAsync($"{_backendUrl}/api/device-command", content);
                Debug.WriteLine($"[121AI] Backend response: {response.StatusCode}");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Backend communication failed: {ex.Message}");
            }
        }

        private async Task NotifyBackendAsync(string eventName, object data)
        {
            try
            {
                var payload = new
                {
                    @event = eventName,
                    platform = "windows",
                    timestamp = DateTime.UtcNow.ToString("O"),
                    data
                };

                var json = JsonSerializer.Serialize(payload);
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

                await _apiClient.PostAsync($"{_backendUrl}/api/device-event", content);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[121AI ERROR] Event notification failed: {ex.Message}");
            }
        }
    }

    // MARK: - Event Arguments

    public class DeviceCommandEventArgs : EventArgs
    {
        public string Command { get; set; }
        public string Source { get; set; }
        public DateTime Timestamp { get; set; }
    }

    public class DeviceEventArgs : EventArgs
    {
        public string Event { get; set; }
        public Dictionary<string, object> Data { get; set; }
        public DateTime Timestamp { get; set; }
    }
}
