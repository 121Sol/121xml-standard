// 121AI iOS Device Integration Layer
// Native access to Calendar, Contacts, Reminders, Tasks, Alarms
// Full Siri integration for voice commands

import Foundation
import EventKit
import Contacts
import UserNotifications
import StoreKit
import Messages

@MainActor
class Agent121AIDeviceIntegration: NSObject {

    // Event store for Calendar and Reminders
    private let eventStore = EKEventStore()
    private let contactStore = CNContactStore()

    // Notification center
    private let notificationCenter = UNUserNotificationCenter.current()

    // API client
    private let apiClient = URLSession.shared
    private let backendUrl = "http://localhost:8000"

    // Intents for Siri
    var siriIntents: [String] = [
        "Create Calendar Event",
        "Add Reminder",
        "Set Alarm",
        "List Today's Tasks",
        "Launch App",
        "Schedule Video Call",
        "Find Contact"
    ]

    override init() {
        super.init()
        requestCalendarAccess()
        requestReminderAccess()
        requestContactAccess()
        requestNotificationAccess()
    }

    // MARK: - Permission Management

    private func requestCalendarAccess() {
        Task {
            do {
                try await eventStore.requestFullAccessToEvents()
            } catch {
                print("[121AI] Calendar access denied: \(error.localizedDescription)")
            }
        }
    }

    private func requestReminderAccess() {
        Task {
            do {
                try await eventStore.requestFullAccessToReminders()
            } catch {
                print("[121AI] Reminder access denied: \(error.localizedDescription)")
            }
        }
    }

    private func requestContactAccess() {
        Task {
            do {
                try await contactStore.requestAccess(for: .contacts)
            } catch {
                print("[121AI] Contact access denied: \(error.localizedDescription)")
            }
        }
    }

    private func requestNotificationAccess() {
        notificationCenter.requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                DispatchQueue.main.async {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
        }
    }

    // MARK: - Calendar Integration

    /// Create calendar event with multiple participants
    /// Example: "Add meeting with George Bush and Tony Blair at the White House Oval Room"
    func createCalendarEvent(title: String,
                            description: String,
                            date: Date,
                            duration: TimeInterval = 3600,
                            participants: [String],
                            location: String = "") async throws -> EKEvent {

        let event = EKEvent(eventStore: eventStore)
        event.title = title
        event.notes = description
        event.startDate = date
        event.endDate = Date(timeInterval: duration, since: date)
        event.location = location

        // Add participants as attendees
        for participantName in participants {
            if let contact = try findContact(by: participantName) {
                if let email = contact.emailAddresses.first?.value as? String {
                    let attendee = EKParticipant()
                    // Note: Direct attendee creation is limited; use calendar invitations instead
                }
            }
        }

        // Find default calendar or create in preferred calendar
        if let calendar = eventStore.defaultCalendarForNewEvents {
            event.calendar = calendar
            try eventStore.save(event, span: .thisEvent, commit: true)

            // Send to 121AI backend for processing
            await notifyBackend(event: "calendar.created", data: [
                "title": title,
                "participants": participants,
                "location": location,
                "date": ISO8601DateFormatter().string(from: date)
            ])
        }

        return event
    }

    /// List today's calendar events
    func listTodaysEvents() async throws -> [EKEvent] {
        let startDate = Calendar.current.startOfDay(for: Date())
        let endDate = Calendar.current.date(byAdding: .day, value: 1, to: startDate)!

        let predicate = eventStore.predicateForEvents(
            withStart: startDate,
            end: endDate,
            calendars: eventStore.calendars(for: .event)
        )

        return eventStore.events(matching: predicate)
    }

    /// Search calendar events
    func searchEvents(query: String) async throws -> [EKEvent] {
        let allCalendars = eventStore.calendars(for: .event)
        let predicate = eventStore.predicateForEvents(
            withStart: Date(timeIntervalSinceNow: -30*24*3600),
            end: Date(timeIntervalSinceNow: 365*24*3600),
            calendars: allCalendars
        )

        let events = eventStore.events(matching: predicate)
        return events.filter {
            $0.title.localizedCaseInsensitiveContains(query) ||
            $0.location?.localizedCaseInsensitiveContains(query) ?? false
        }
    }

    // MARK: - Reminders Integration

    /// Add reminder
    /// Example: "Remind me to call the Prime Minister of Pakistan"
    func addReminder(title: String,
                     description: String = "",
                     dueDate: Date? = nil,
                     priority: EKAlarm = EKAlarm(relativeOffset: -3600)) async throws -> EKReminder {

        let reminder = EKReminder(eventStore: eventStore)
        reminder.title = title
        reminder.notes = description

        if let dueDate = dueDate {
            let alarmDate = Calendar.current.dateComponents(
                [.year, .month, .day, .hour, .minute],
                from: dueDate
            )
            reminder.dueDateComponents = alarmDate
            reminder.addAlarm(priority)
        }

        // Save to default reminder list
        if let calendarList = eventStore.calendars(for: .reminder).first {
            reminder.calendar = calendarList
            try eventStore.save(reminder, commit: true)

            // Notify backend
            await notifyBackend(event: "reminder.created", data: [
                "title": title,
                "dueDate": dueDate.map { ISO8601DateFormatter().string(from: $0) } ?? ""
            ])
        }

        return reminder
    }

    /// List today's reminders
    func listTodaysReminders() async throws -> [EKReminder] {
        let startDate = Calendar.current.startOfDay(for: Date())
        let endDate = Calendar.current.date(byAdding: .day, value: 1, to: startDate)!

        let predicate = eventStore.predicateForReminders(
            in: eventStore.calendars(for: .reminder)
        )

        let reminders = eventStore.reminders(matching: predicate)
        return reminders.filter { reminder in
            guard let dueDate = reminder.dueDateComponents else { return true }
            if let date = Calendar.current.date(from: dueDate) {
                return date >= startDate && date <= endDate
            }
            return false
        }
    }

    // MARK: - Alarms Integration

    /// Set alarm
    /// Example: "Set an alarm for 7 AM tomorrow"
    func setAlarm(time: Date, label: String = "121AI Alarm") async throws {
        let notification = UNMutableNotificationContent()
        notification.title = label
        notification.sound = .default
        notification.badge = NSNumber(value: UIApplication.shared.applicationIconBadgeNumber + 1)

        // Calculate time interval
        let interval = time.timeIntervalSinceNow

        if interval > 0 {
            let trigger = UNTimeIntervalNotificationTrigger(timeInterval: interval, repeats: false)
            let request = UNNotificationRequest(identifier: UUID().uuidString, content: notification, trigger: trigger)

            try await notificationCenter.add(request)

            // Notify backend
            await notifyBackend(event: "alarm.set", data: [
                "time": ISO8601DateFormatter().string(from: time),
                "label": label
            ])
        }
    }

    /// Cancel alarm
    func cancelAlarm(identifier: String) {
        notificationCenter.removePendingNotificationRequests(withIdentifiers: [identifier])
    }

    // MARK: - Contacts Integration

    /// Find contact by name or email
    func findContact(by nameOrEmail: String) async throws -> CNContact? {
        let keysToFetch = [CNContactGivenNameKey, CNContactFamilyNameKey,
                          CNContactPhoneNumbersKey, CNContactEmailAddressesKey]

        let predicate = CNContact.predicateForContacts(matchingName: nameOrEmail)
        let contacts = try contactStore.unifiedContacts(matching: predicate, keysToFetch: keysToFetch as [CNKeyDescriptor])

        return contacts.first
    }

    /// Get all contacts
    func getAllContacts() async throws -> [CNContact] {
        let keysToFetch = [CNContactGivenNameKey, CNContactFamilyNameKey,
                          CNContactPhoneNumbersKey, CNContactEmailAddressesKey]

        let request = CNContactFetchRequest(keysToFetch: keysToFetch as [CNKeyDescriptor])
        var contacts: [CNContact] = []

        try contactStore.enumerateContacts(with: request) { contact in
            contacts.append(contact)
        }

        return contacts
    }

    /// Get contact phone number
    func getContactPhone(_ contact: CNContact) -> String? {
        return contact.phoneNumbers.first?.value.stringValue
    }

    /// Get contact email
    func getContactEmail(_ contact: CNContact) -> String? {
        return contact.emailAddresses.first?.value as? String
    }

    // MARK: - App Launching

    /// Launch app by name or bundle identifier
    /// Example: "Launch Google Meet"
    func launchApp(name: String) async throws {
        let urlSchemes = [
            "google meet": "googlemeet://",
            "zoom": "zoommtg://",
            "facetime": "facetime://",
            "phone": "tel://",
            "messages": "sms://",
            "mail": "mailto://",
            "notes": "mobilenotes://",
            "reminders": "mobilecal://"
        ]

        let lowercaseName = name.lowercased()

        if let urlScheme = urlSchemes.first(where: { lowercaseName.contains($0.key) })?.value {
            if let url = URL(string: urlScheme), UIApplication.shared.canOpenURL(url) {
                try await UIApplication.shared.open(url)

                // Notify backend
                await notifyBackend(event: "app.launched", data: ["app": name])
                return
            }
        }

        throw NSError(domain: "App Launch", code: -1,
                     userInfo: [NSLocalizedDescriptionKey: "App not found: \(name)"])
    }

    // MARK: - Video Conference Integration

    /// Schedule video call with multiple participants
    /// Example: "Schedule a Google Meet with Prime Ministers of Pakistan and Iran"
    func scheduleVideoCall(title: String,
                          participants: [String],
                          startTime: Date,
                          platform: String = "google_meet") async throws {

        var eventData: [String: Any] = [
            "title": title,
            "participants": participants,
            "startTime": ISO8601DateFormatter().string(from: startTime),
            "platform": platform
        ]

        // Create calendar event
        let event = try await createCalendarEvent(
            title: "\(title) - Video Call",
            description: "Video conference with \(participants.joined(separator: ", "))",
            date: startTime,
            participants: participants,
            location: "Online - \(platform)"
        )

        // Get conference link based on platform
        var conferenceUrl = ""
        switch platform.lowercased() {
        case "google_meet":
            conferenceUrl = "https://meet.google.com/\(UUID().uuidString.prefix(10))"
        case "zoom":
            conferenceUrl = "https://zoom.us/j/\(Int.random(in: 100000000...999999999))"
        default:
            conferenceUrl = "https://conference.example.com/\(event.eventIdentifier)"
        }

        eventData["conferenceUrl"] = conferenceUrl

        // Send invitations to participants
        for participant in participants {
            if let contact = try await findContact(by: participant),
               let email = getContactEmail(contact) {
                await sendVideoCallInvite(to: email, title: title, url: conferenceUrl)
            }
        }

        // Notify backend
        await notifyBackend(event: "video_call.scheduled", data: eventData)
    }

    /// Send video call invitation
    private func sendVideoCallInvite(to email: String, title: String, url: String) async {
        let inviteData: [String: Any] = [
            "recipient": email,
            "title": title,
            "conferenceUrl": url,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]

        await notifyBackend(event: "video_invite.sent", data: inviteData)
    }

    // MARK: - Siri Intent Handling

    /// Process Siri voice command
    /// Example: "Siri, ask 121AI to list today's tasks"
    func processSiriCommand(_ command: String) async throws {
        // Send to 121AI backend for natural language processing
        try await sendToBackend(command: command, source: "siri")

        let parsedCommand = await parseCommand(command)

        // Route to appropriate handler
        switch parsedCommand.intent {
        case "create_event":
            if let eventData = parsedCommand.data as? [String: Any] {
                _ = try await createCalendarEvent(
                    title: eventData["title"] as? String ?? "",
                    description: eventData["description"] as? String ?? "",
                    date: eventData["date"] as? Date ?? Date(),
                    participants: eventData["participants"] as? [String] ?? [],
                    location: eventData["location"] as? String ?? ""
                )
            }

        case "add_reminder":
            if let reminderData = parsedCommand.data as? [String: Any] {
                _ = try await addReminder(
                    title: reminderData["title"] as? String ?? "",
                    dueDate: reminderData["dueDate"] as? Date
                )
            }

        case "set_alarm":
            if let alarmData = parsedCommand.data as? [String: Any] {
                try await setAlarm(
                    time: alarmData["time"] as? Date ?? Date(),
                    label: alarmData["label"] as? String ?? ""
                )
            }

        case "list_events":
            let events = try await listTodaysEvents()
            let eventList = events.map { $0.title }.joined(separator: ", ")
            await speakResponse("Today's events: \(eventList)")

        case "launch_app":
            if let appName = parsedCommand.data as? String {
                try await launchApp(name: appName)
            }

        case "schedule_video_call":
            if let callData = parsedCommand.data as? [String: Any] {
                try await scheduleVideoCall(
                    title: callData["title"] as? String ?? "",
                    participants: callData["participants"] as? [String] ?? [],
                    startTime: callData["startTime"] as? Date ?? Date(),
                    platform: callData["platform"] as? String ?? "google_meet"
                )
            }

        default:
            await speakResponse("Command not recognized")
        }
    }

    // MARK: - Command Parsing

    private func parseCommand(_ command: String) async -> (intent: String, data: Any?) {
        do {
            var request = URLRequest(url: URL(string: "\(backendUrl)/api/parse-intent")!)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")

            let payload = ["command": command, "platform": "siri"]
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)

            let (data, _) = try await URLSession.shared.data(for: request)

            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let intent = json["intent"] as? String {
                return (intent, json["data"])
            }
        } catch {
            print("[121AI] Command parsing error: \(error.localizedDescription)")
        }

        return ("unknown", nil)
    }

    // MARK: - Backend Communication

    private func sendToBackend(command: String, source: String) async throws {
        var request = URLRequest(url: URL(string: "\(backendUrl)/api/device-command")!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload: [String: Any] = [
            "command": command,
            "source": source,
            "platform": "ios",
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]

        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (_, response) = try await URLSession.shared.data(for: request)

        if let httpResponse = response as? HTTPURLResponse {
            print("[121AI] Backend response: \(httpResponse.statusCode)")
        }
    }

    private func notifyBackend(event: String, data: [String: Any]) async {
        var request = URLRequest(url: URL(string: "\(backendUrl)/api/device-event")!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        var payload = data
        payload["event"] = event
        payload["platform"] = "ios"
        payload["timestamp"] = ISO8601DateFormatter().string(from: Date())

        request.httpBody = try? JSONSerialization.data(withJSONObject: payload)

        _ = try? await URLSession.shared.data(for: request)
    }

    private func speakResponse(_ text: String) async {
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        AVSpeechSynthesizer().speak(utterance)
    }
}
