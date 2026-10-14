
# Keep all serializable models and Room entities intact for JSON streaming
-keepclassmembers class com.example.model.** { *; }
-keep class com.example.model.** { *; }
-keep class com.example.database.** { *; }
-keep class com.example.repository.** { *; }
-keep class com.example.updater.** { *; }

# Preserve serialized names for Moshi / Gson
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

# Basic Gson & reflection rules
-keep class com.google.gson.** { *; }
-keep class sun.misc.Unsafe { *; }
-keep class com.google.gson.stream.** { *; }

# Repackage & obfuscate core business logic and evaluators
-repackageclasses 'com.example.shield'
-allowaccessmodification
