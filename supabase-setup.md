# Supabase Setup Guide for CTAS

## 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in to your account
3. Click "New Project"
4. Fill in project details:
   - **Name**: `coastal-threat-alert-system`
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your users
5. Wait for project creation (2-3 minutes)

## 2. Get Project Credentials

After project creation, go to **Settings > API**:

- **Project URL**: `https://your-project-ref.supabase.co`
- **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (public key)
- **Service Role Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (secret key)

## 3. Database Schema Setup

Run these SQL commands in the Supabase SQL Editor:

```sql
-- Enable Row Level Security
ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;

-- Create users table (extends auth.users)
CREATE TABLE public.users (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  phone_number TEXT,
  role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create locations table
CREATE TABLE public.locations (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  latitude DECIMAL(10, 8) NOT NULL,
  longitude DECIMAL(11, 8) NOT NULL,
  address TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create alerts table
CREATE TABLE public.alerts (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  location_id INTEGER REFERENCES public.locations(id) ON DELETE CASCADE,
  alert_type TEXT NOT NULL CHECK (alert_type IN ('flood', 'storm_surge', 'tsunami', 'cyclone')),
  severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE
);

-- Create forecasts table
CREATE TABLE public.forecasts (
  id SERIAL PRIMARY KEY,
  location_id INTEGER REFERENCES public.locations(id) ON DELETE CASCADE,
  forecast_type TEXT NOT NULL CHECK (forecast_type IN ('flood', 'storm_surge', 'weather')),
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  forecast_data JSONB,
  confidence_score DECIMAL(3, 2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  forecast_time TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Create time_series_data table
CREATE TABLE public.time_series_data (
  id SERIAL PRIMARY KEY,
  forecast_id INTEGER REFERENCES public.forecasts(id) ON DELETE CASCADE,
  data_type TEXT NOT NULL CHECK (data_type IN ('water_level', 'wave_height', 'wind_speed', 'precipitation')),
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  value DECIMAL(10, 4) NOT NULL,
  unit TEXT NOT NULL,
  metadata JSONB
);

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.time_series_data ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- Locations policies
CREATE POLICY "Users can view own locations" ON public.locations
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own locations" ON public.locations
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own locations" ON public.locations
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own locations" ON public.locations
  FOR DELETE USING (auth.uid() = user_id);

-- Alerts policies
CREATE POLICY "Users can view own alerts" ON public.alerts
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own alerts" ON public.alerts
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Forecasts policies (read-only for users, managed by system)
CREATE POLICY "Users can view forecasts for their locations" ON public.forecasts
  FOR SELECT USING (
    location_id IN (
      SELECT id FROM public.locations WHERE user_id = auth.uid()
    )
  );

-- Time series data policies
CREATE POLICY "Users can view time series for their forecasts" ON public.time_series_data
  FOR SELECT USING (
    forecast_id IN (
      SELECT f.id FROM public.forecasts f
      JOIN public.locations l ON f.location_id = l.id
      WHERE l.user_id = auth.uid()
    )
  );

-- Create function to handle user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, full_name)
  VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user creation
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

## 4. Authentication Configuration

In Supabase Dashboard:

1. Go to **Authentication > Settings**
2. Configure **Site URL**: `http://localhost:3000` (for development)
3. Add **Redirect URLs**:
   - `http://localhost:3000/auth/callback`
   - `http://localhost:3000/reset-password`
4. Enable **Email confirmations** if desired
5. Configure **Email templates** as needed

## 5. Update Environment Variables

Update your `.env` files with the actual Supabase credentials:

### Frontend (.env)
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

### Backend (.env)
```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-service-role-key-here
```

## 6. Test Authentication

1. Start both frontend and backend servers
2. Navigate to `/register` and create a test account
3. Check Supabase Dashboard > Authentication > Users to see the new user
4. Test login/logout functionality

## 7. Production Setup

For production deployment:

1. Update **Site URL** to your production domain
2. Add production **Redirect URLs**
3. Configure custom SMTP for emails (optional)
4. Set up database backups
5. Configure proper RLS policies for your use case

## Security Notes

- Never expose the **Service Role Key** in frontend code
- Use **Anon Key** only in frontend applications
- Always enable Row Level Security (RLS) on tables
- Regularly rotate API keys
- Monitor authentication logs in Supabase Dashboard