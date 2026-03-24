# GymApp Memory

## Project Overview
React Native gym tracker app with AI workout generation (Groq/Llama) and Firebase backend.
Working directory: `/Users/basargorgundur/Desktop/GymApp`
Current worktree: `.claude/worktrees/strange-benz` (branch: `claude/strange-benz`)

## Architecture
- **Navigation**: Manual prop-drilling via `screenProps` in App.js (not React Navigation stack)
- **Auth**: Firebase Auth (`@react-native-firebase/auth`) — real email/password + guest mode (AsyncStorage-only)
- **Storage**: Dual-layer — AsyncStorage (local cache/offline) + Firestore (cloud sync)
- **AI**: Groq API with Llama 3.3 70B via `src/services/LLMService.js`
- **Exercises**: ExerciseDB API with 24hr AsyncStorage cache in `src/services/ExerciseAPI.js`

## Key Files
- `App.js` — auth state listener via `auth().onAuthStateChanged`, passes `uid` through all screenProps
- `src/services/FirestoreService.js` — all Firestore ops (profile, history, programs, migration)
- `src/services/firebase.js` — Firebase imports/exports
- `src/screens/LoginScreen.js` — Firebase Auth login/signup/forgot-password + guest mode
- `src/screens/ProfileScreen.js` — syncs to Firestore via `saveProfile()` in App.js
- `src/screens/GeneratedWorkoutScreen.js` — saves completed workouts to Firestore
- `src/screens/WorkoutScreen.js` — saves AI/user programs to Firestore
- `src/screens/ProgramsScreen.js` — loads programs & history from Firestore

## Firestore Schema
```
users/{uid}                          — user metadata
users/{uid}/settings/profile         — user profile/preferences (single doc)
users/{uid}/workoutHistory/{auto-id} — completed workouts
users/{uid}/programs/{programId}     — saved programs (daily/weekly/AI)
```

## AsyncStorage Keys
- `user_data` — guest session data
- `user_profile` — fitness preferences (local cache)
- `user_info` — full personal info (local cache)
- `workout_history` — local workout history cache
- `workout_programs_v2` — local programs cache
- `today_workout_${date}` — today's exercise list
- `current_workout_state` — in-progress workout
- `firebase_migrated_{uid}` — migration flag

## Completed Improvements
1. **Firebase Integration** (worktree `strange-benz`) — real auth, Firestore cloud sync, data migration, forgot password
2. Next planned: Progress/strength tracking using Firestore workout history

## Guest Mode
Guest users use AsyncStorage only — no Firebase involved. Handled in App.js `onAuthStateChanged`.
