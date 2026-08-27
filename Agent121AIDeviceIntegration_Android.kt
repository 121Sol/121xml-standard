// 121AI Android Device Integration Layer
// Native access to Calendar, Contacts, Tasks, Alarms
// Full Google Assistant integration

package com.agent121ai.mobile

import android.content.Context
import android.content.Intent
import android.provider.CalendarContract
import android.provider.ContactsContract
import android.provider.AlarmClock
import android.app.AlarmManager
import android.app.PendingIntent
import android.content.pm.PackageManager
import android.os.Build
import android.Manifest
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import android.database.Cursor
import android.net.Uri
import kotlinx.coroutines.*
import okhttp3.*
import java.time.LocalDateTime
import java.time.ZoneId
import java.util.*
import com.google.gson.JsonObject

/**
 * 121AI Android Device Integration
 * Unified access to native device capabilities through Google Assistant
 */
class Agent121AIDeviceIntegration(private val context: Context) {

    private val apiClient = OkHttpClient()
    private val backendUrl = "http://192.168.1.100:8000"
    private val scope = CoroutineScope(Dispatchers.Main + Job())

    // System managers
    private val calendarResolver = context.contentResolver
    private val contactResolver = context.contentResolver
    private val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
    private val packageManager = context.packageManager

    init {
        requestPermissions()
    }

    // MARK: - Permission Management

    private fun requestPermissions() {
        val requiredPermissions = listOf(
            Manifest.permission.READ_CALENDAR,
            Manifest.permission.WRITE_CALENDAR,
            Manifest.permission.READ_CONTACTS,
            Manifest.permission.SCHEDULE_EXACT_ALARM,
            Manifest.permission.POST_NOTIFICATIONS,
            Manifest.permission.INTERNET
        )

        requiredPermissions.forEach { permission ->
            if (ContextCompat.checkSelfPermission(context, permission)
                != PackageManager.PERMISSION_GRANTED) {
                // Permission not granted, would need to request from Activity
                android.util.Log.d("121AI", "Permission needed: $permission")
            }
        }
    }

    // MARK: - Calendar Integration

    /**
     * Create calendar event with multiple participants
     * Example: "Add meeting with George Bush and Tony Blair at the White House Oval Room"
     */
    suspend fun createCalendarEvent(
        title: String,
        description: String,
        startTime: Long,
        endTime: Long,
        participants: List<String>,
        location: String = ""
    ): Boolean = withContext(Dispatchers.IO) {
        try {
            val contentValues = android.content.ContentValues().apply {
                put(CalendarContract.Events.TITLE, title)
                put(CalendarContract.Events.DESCRIPTION, description)
                put(CalendarContract.Events.DTSTART, startTime)
                put(CalendarContract.Events.DTEND, endTime)
                put(CalendarContract.Events.LOCATION, location)
                put(CalendarContract.Events.CALENDAR_ID, getDefaultCalendarId())
                put(CalendarContract.Events.EVENT_TIMEZONE, TimeZone.getDefault().id)
            }

            val uri = calendarResolver.insert(CalendarContract.Events.CONTENT_URI, contentValues)

            if (uri != null) {
                // Add participants as attendees
                for (participant in participants) {
                    val contact = findContact(participant)
                    contact?.let { addAttendee(uri, it) }
                }

                // Notify backend
                notifyBackendAsync(
                    "calendar.created",
                    mapOf(
                        "title" to title,
                        "participants" to participants.joinToString(", "),
                        "location" to location,
                        "timestamp" to System.currentTimeMillis()
                    )
                )
                return@withContext true
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Calendar creation error: ${e.message}")
        }
        false
    }

    /**
     * List today's calendar events
     */
    suspend fun listTodaysEvents(): List<CalendarEvent> = withContext(Dispatchers.IO) {
        val events = mutableListOf<CalendarEvent>()
        try {
            val calendar = Calendar.getInstance()
            val startTime = calendar.apply { set(Calendar.HOUR_OF_DAY, 0) }.timeInMillis
            val endTime = calendar.apply { add(Calendar.DAY_OF_MONTH, 1) }.timeInMillis

            val projection = arrayOf(
                CalendarContract.Events._ID,
                CalendarContract.Events.TITLE,
                CalendarContract.Events.DTSTART,
                CalendarContract.Events.DTEND,
                CalendarContract.Events.LOCATION
            )

            val selection = "(${CalendarContract.Events.DTSTART} >= ? AND ${CalendarContract.Events.DTSTART} <= ?)"
            val selectionArgs = arrayOf(startTime.toString(), endTime.toString())

            val cursor: Cursor? = calendarResolver.query(
                CalendarContract.Events.CONTENT_URI,
                projection,
                selection,
                selectionArgs,
                null
            )

            cursor?.use {
                while (it.moveToNext()) {
                    events.add(
                        CalendarEvent(
                            id = it.getLong(0),
                            title = it.getString(1),
                            startTime = it.getLong(2),
                            endTime = it.getLong(3),
                            location = it.getString(4) ?: ""
                        )
                    )
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "List events error: ${e.message}")
        }
        events
    }

    /**
     * Search calendar events
     */
    suspend fun searchEvents(query: String): List<CalendarEvent> = withContext(Dispatchers.IO) {
        val events = mutableListOf<CalendarEvent>()
        try {
            val projection = arrayOf(
                CalendarContract.Events._ID,
                CalendarContract.Events.TITLE,
                CalendarContract.Events.DTSTART,
                CalendarContract.Events.DTEND,
                CalendarContract.Events.LOCATION
            )

            val selection = "(${CalendarContract.Events.TITLE} LIKE ?)"
            val selectionArgs = arrayOf("%$query%")

            val cursor = calendarResolver.query(
                CalendarContract.Events.CONTENT_URI,
                projection,
                selection,
                selectionArgs,
                null
            )

            cursor?.use {
                while (it.moveToNext()) {
                    events.add(
                        CalendarEvent(
                            id = it.getLong(0),
                            title = it.getString(1),
                            startTime = it.getLong(2),
                            endTime = it.getLong(3),
                            location = it.getString(4) ?: ""
                        )
                    )
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Search events error: ${e.message}")
        }
        events
    }

    // MARK: - Alarms Integration

    /**
     * Set alarm
     * Example: "Set an alarm for 7 AM tomorrow"
     */
    suspend fun setAlarm(
        hour: Int,
        minute: Int,
        label: String = "121AI Alarm",
        days: List<Int> = emptyList()
    ): Boolean = withContext(Dispatchers.IO) {
        try {
            val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
                putExtra(AlarmClock.EXTRA_HOUR, hour)
                putExtra(AlarmClock.EXTRA_MINUTES, minute)
                putExtra(AlarmClock.EXTRA_MESSAGE, label)
                if (days.isNotEmpty()) {
                    putExtra(AlarmClock.EXTRA_DAYS, days)
                }
            }

            if (intent.resolveActivity(packageManager) != null) {
                context.startActivity(intent)

                // Notify backend
                notifyBackendAsync(
                    "alarm.set",
                    mapOf(
                        "time" to "$hour:$minute",
                        "label" to label,
                        "timestamp" to System.currentTimeMillis()
                    )
                )
                return@withContext true
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Set alarm error: ${e.message}")
        }
        false
    }

    /**
     * Create timer
     * Example: "Set a 10-minute timer"
     */
    suspend fun createTimer(durationSeconds: Int, label: String = "121AI Timer"): Boolean = withContext(Dispatchers.IO) {
        try {
            val intent = Intent(AlarmClock.ACTION_SET_TIMER).apply {
                putExtra(AlarmClock.EXTRA_LENGTH, durationSeconds)
                putExtra(AlarmClock.EXTRA_MESSAGE, label)
                putExtra(AlarmClock.EXTRA_SKIP_UI, false)
            }

            if (intent.resolveActivity(packageManager) != null) {
                context.startActivity(intent)

                notifyBackendAsync(
                    "timer.created",
                    mapOf(
                        "duration" to durationSeconds,
                        "label" to label
                    )
                )
                return@withContext true
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Create timer error: ${e.message}")
        }
        false
    }

    // MARK: - Contacts Integration

    /**
     * Find contact by name or email
     */
    fun findContact(nameOrEmail: String): Contact? {
        try {
            val projection = arrayOf(
                ContactsContract.Contacts._ID,
                ContactsContract.Contacts.DISPLAY_NAME,
                ContactsContract.Contacts.HAS_PHONE_NUMBER
            )

            val selection = "(${ContactsContract.Contacts.DISPLAY_NAME} LIKE ?)"
            val selectionArgs = arrayOf("%$nameOrEmail%")

            val cursor = contactResolver.query(
                ContactsContract.Contacts.CONTENT_URI,
                projection,
                selection,
                selectionArgs,
                null
            )

            cursor?.use {
                if (it.moveToFirst()) {
                    val id = it.getLong(0)
                    val displayName = it.getString(1)
                    val hasPhone = it.getInt(2) > 0

                    return Contact(
                        id = id,
                        displayName = displayName,
                        phone = if (hasPhone) getContactPhone(id) else null,
                        email = getContactEmail(id)
                    )
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Find contact error: ${e.message}")
        }
        return null
    }

    /**
     * Get contact phone number
     */
    private fun getContactPhone(contactId: Long): String? {
        try {
            val phoneCursor = contactResolver.query(
                ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                arrayOf(ContactsContract.CommonDataKinds.Phone.NUMBER),
                "${ContactsContract.CommonDataKinds.Phone.CONTACT_ID} = ?",
                arrayOf(contactId.toString()),
                null
            )

            phoneCursor?.use {
                if (it.moveToFirst()) {
                    return it.getString(0)
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Get phone error: ${e.message}")
        }
        return null
    }

    /**
     * Get contact email
     */
    private fun getContactEmail(contactId: Long): String? {
        try {
            val emailCursor = contactResolver.query(
                ContactsContract.CommonDataKinds.Email.CONTENT_URI,
                arrayOf(ContactsContract.CommonDataKinds.Email.ADDRESS),
                "${ContactsContract.CommonDataKinds.Email.CONTACT_ID} = ?",
                arrayOf(contactId.toString()),
                null
            )

            emailCursor?.use {
                if (it.moveToFirst()) {
                    return it.getString(0)
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Get email error: ${e.message}")
        }
        return null
    }

    // MARK: - App Launching

    /**
     * Launch app by package name
     * Example: "Launch Google Meet"
     */
    suspend fun launchApp(appName: String): Boolean = withContext(Dispatchers.Main) {
        try {
            val packageName = mapAppNameToPackage(appName)

            val launchIntent = packageManager.getLaunchIntentForPackage(packageName)
            if (launchIntent != null) {
                context.startActivity(launchIntent)

                notifyBackendAsync(
                    "app.launched",
                    mapOf("app" to appName)
                )
                return@withContext true
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Launch app error: ${e.message}")
        }
        false
    }

    private fun mapAppNameToPackage(appName: String): String {
        return when (appName.lowercase()) {
            "google meet", "meet" -> "com.google.android.apps.meetings"
            "zoom" -> "us.zoom.videomeetings"
            "phone", "phone call" -> "com.android.phone"
            "messages", "sms" -> "com.android.messaging"
            "mail", "gmail" -> "com.google.android.gm"
            "calendar" -> "com.google.android.calendar"
            "contacts" -> "com.android.contacts"
            "notes" -> "com.google.android.keep"
            "google maps", "maps" -> "com.google.android.apps.maps"
            "youtube" -> "com.google.android.youtube"
            else -> appName
        }
    }

    // MARK: - Video Conference Integration

    /**
     * Schedule video call with multiple participants
     * Example: "Schedule a Google Meet with Prime Ministers of Pakistan and Iran"
     */
    suspend fun scheduleVideoCall(
        title: String,
        participants: List<String>,
        startTime: Long,
        platform: String = "google_meet"
    ): Boolean = withContext(Dispatchers.IO) {
        try {
            // Create calendar event
            val created = createCalendarEvent(
                title = "$title - Video Call",
                description = "Video conference with ${participants.joinToString(", ")}",
                startTime = startTime,
                endTime = startTime + 3600000, // 1 hour
                participants = participants,
                location = "Online - $platform"
            )

            if (created) {
                // Generate conference URL
                val conferenceUrl = when (platform.lowercase()) {
                    "google_meet" -> "https://meet.google.com/${UUID.randomUUID().toString().take(10)}"
                    "zoom" -> "https://zoom.us/j/${(Math.random() * 1000000000).toLong()}"
                    else -> "https://conference.example.com/${UUID.randomUUID()}"
                }

                // Send notifications to participants
                for (participant in participants) {
                    val contact = findContact(participant)
                    contact?.email?.let {
                        sendVideoCallInvite(it, title, conferenceUrl)
                    }
                }

                notifyBackendAsync(
                    "video_call.scheduled",
                    mapOf(
                        "title" to title,
                        "participants" to participants.joinToString(", "),
                        "platform" to platform,
                        "conferenceUrl" to conferenceUrl
                    )
                )
                return@withContext true
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Schedule video call error: ${e.message}")
        }
        false
    }

    private fun sendVideoCallInvite(email: String, title: String, url: String) {
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "message/rfc822"
            putExtra(Intent.EXTRA_EMAIL, arrayOf(email))
            putExtra(Intent.EXTRA_SUBJECT, "Invitation: $title")
            putExtra(Intent.EXTRA_TEXT, "Join the video call: $url")
        }

        context.startActivity(Intent.createChooser(intent, "Send Invitation"))
    }

    // MARK: - Google Assistant Integration

    /**
     * Process Google Assistant voice command
     * Example: "Hey Google, ask 121AI to list today's tasks"
     */
    suspend fun processAssistantCommand(command: String) = withContext(Dispatchers.IO) {
        try {
            sendToBackend(
                command = command,
                source = "google_assistant",
                platform = "android"
            )

            val parsedCommand = parseCommand(command)

            when (parsedCommand.first) {
                "create_event" -> {
                    // Extract event data and create
                    val eventData = parsedCommand.second as? Map<*, *>
                    eventData?.let {
                        createCalendarEvent(
                            title = it["title"] as? String ?: "",
                            description = it["description"] as? String ?: "",
                            startTime = (it["startTime"] as? Number)?.toLong() ?: System.currentTimeMillis(),
                            endTime = (it["endTime"] as? Number)?.toLong() ?: System.currentTimeMillis() + 3600000,
                            participants = (it["participants"] as? List<*>)?.mapNotNull { p -> p as? String } ?: emptyList(),
                            location = it["location"] as? String ?: ""
                        )
                    }
                }

                "list_events" -> {
                    val events = listTodaysEvents()
                    val eventTitles = events.map { it.title }.joinToString(", ")
                    speakResponse("Today's events: $eventTitles")
                }

                "set_alarm" -> {
                    val alarmData = parsedCommand.second as? Map<*, *>
                    alarmData?.let {
                        val hour = (it["hour"] as? Number)?.toInt() ?: 7
                        val minute = (it["minute"] as? Number)?.toInt() ?: 0
                        setAlarm(hour, minute, it["label"] as? String ?: "121AI Alarm")
                    }
                }

                "launch_app" -> {
                    val appName = parsedCommand.second as? String
                    appName?.let { launchApp(it) }
                }

                "schedule_video_call" -> {
                    val callData = parsedCommand.second as? Map<*, *>
                    callData?.let {
                        scheduleVideoCall(
                            title = it["title"] as? String ?: "",
                            participants = (it["participants"] as? List<*>)?.mapNotNull { p -> p as? String } ?: emptyList(),
                            startTime = (it["startTime"] as? Number)?.toLong() ?: System.currentTimeMillis(),
                            platform = it["platform"] as? String ?: "google_meet"
                        )
                    }
                }

                else -> speakResponse("Command not recognized")
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Process command error: ${e.message}")
        }
    }

    // MARK: - Backend Communication

    private suspend fun parseCommand(command: String): Pair<String, Any?> = withContext(Dispatchers.IO) {
        try {
            val jsonPayload = JsonObject().apply {
                addProperty("command", command)
                addProperty("platform", "android")
            }

            val body = RequestBody.create(
                MediaType.parse("application/json"),
                jsonPayload.toString()
            )

            val request = Request.Builder()
                .url("$backendUrl/api/parse-intent")
                .post(body)
                .build()

            apiClient.newCall(request).execute().use { response ->
                if (response.isSuccessful) {
                    val json = response.body()?.string()?.let {
                        com.google.gson.JsonParser.parseString(it).asJsonObject
                    }
                    json?.let {
                        return@withContext Pair(
                            it.get("intent")?.asString ?: "unknown",
                            it.get("data")?.asJsonObject
                        )
                    }
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Parse command error: ${e.message}")
        }
        Pair("unknown", null)
    }

    private suspend fun sendToBackend(command: String, source: String, platform: String) = withContext(Dispatchers.IO) {
        try {
            val jsonPayload = JsonObject().apply {
                addProperty("command", command)
                addProperty("source", source)
                addProperty("platform", platform)
                addProperty("timestamp", System.currentTimeMillis())
            }

            val body = RequestBody.create(
                MediaType.parse("application/json"),
                jsonPayload.toString()
            )

            val request = Request.Builder()
                .url("$backendUrl/api/device-command")
                .post(body)
                .build()

            apiClient.newCall(request).execute()
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Send to backend error: ${e.message}")
        }
    }

    private fun notifyBackendAsync(event: String, data: Map<String, Any?>) {
        scope.launch(Dispatchers.IO) {
            try {
                val jsonPayload = JsonObject().apply {
                    addProperty("event", event)
                    addProperty("platform", "android")
                    addProperty("timestamp", System.currentTimeMillis())
                    data.forEach { (key, value) ->
                        addProperty(key, value?.toString())
                    }
                }

                val body = RequestBody.create(
                    MediaType.parse("application/json"),
                    jsonPayload.toString()
                )

                val request = Request.Builder()
                    .url("$backendUrl/api/device-event")
                    .post(body)
                    .build()

                apiClient.newCall(request).execute()
            } catch (e: Exception) {
                android.util.Log.e("121AI", "Notify backend error: ${e.message}")
            }
        }
    }

    private fun speakResponse(text: String) {
        // Text-to-speech response
        android.util.Log.i("121AI", "Speaking: $text")
    }

    // MARK: - Helper Functions

    private fun getDefaultCalendarId(): Long {
        try {
            val projection = arrayOf(CalendarContract.Calendars._ID)
            val selection = "(${CalendarContract.Calendars.VISIBLE} = 1 AND ${CalendarContract.Calendars.IS_PRIMARY} = 1)"

            val cursor = calendarResolver.query(
                CalendarContract.Calendars.CONTENT_URI,
                projection,
                selection,
                null,
                null
            )

            cursor?.use {
                if (it.moveToFirst()) {
                    return it.getLong(0)
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Get calendar ID error: ${e.message}")
        }
        return 1 // Default calendar ID
    }

    private fun addAttendee(eventUri: Uri, contact: Contact) {
        try {
            contact.email?.let { email ->
                val contentValues = android.content.ContentValues().apply {
                    put(CalendarContract.Attendees.EVENT_ID, eventUri.lastPathSegment)
                    put(CalendarContract.Attendees.ATTENDEE_NAME, contact.displayName)
                    put(CalendarContract.Attendees.ATTENDEE_EMAIL, email)
                    put(CalendarContract.Attendees.ATTENDEE_RELATIONSHIP, CalendarContract.Attendees.RELATIONSHIP_ATTENDEE)
                    put(CalendarContract.Attendees.ATTENDEE_TYPE, CalendarContract.Attendees.TYPE_OPTIONAL)
                    put(CalendarContract.Attendees.ATTENDEE_STATUS, CalendarContract.Attendees.ATTENDEE_STATUS_INVITED)
                }

                calendarResolver.insert(CalendarContract.Attendees.CONTENT_URI, contentValues)
            }
        } catch (e: Exception) {
            android.util.Log.e("121AI", "Add attendee error: ${e.message}")
        }
    }
}

// MARK: - Data Classes

data class CalendarEvent(
    val id: Long,
    val title: String,
    val startTime: Long,
    val endTime: Long,
    val location: String
)

data class Contact(
    val id: Long,
    val displayName: String,
    val phone: String? = null,
    val email: String? = null
)
