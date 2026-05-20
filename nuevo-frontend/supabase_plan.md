# Frontend Supabase Integration Plan

## Goal
Connect the React frontend to Supabase to support user authentication and data persistence.

## Steps

1. **Install Dependencies**
   - `npm install @supabase/supabase-js`

2. **Initialize Client**
   - Create `src/lib/supabase.ts` using `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.

3. **Authentication Context**
   - Create `src/contexts/AuthContext.tsx` to manage:
     - `user` object
     - `loading` state
     - `signInWithEmail` / `signOut` methods
     - Automatic session recovery on load

4. **Integration with API**
   - Update `ResultadosPage.tsx` to:
     - Consume `AuthContext`
     - Get `user.id`
     - Append `X-User-Id` header when calling `/api/analyze`

5. **Profile Management (Optional MVP)**
   - Create a simple hook to fetch/save user profile data to `public.users` table.
