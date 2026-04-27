create table if not exists public.dashboard_current (
  dashboard_slug text primary key,
  generated_at timestamptz,
  executed_at timestamptz,
  project_stage text,
  dashboard_stage text,
  records_total integer,
  radar_matches integer,
  investment_attack_now integer,
  payload jsonb not null
);

create table if not exists public.dashboard_history (
  id bigint generated always as identity primary key,
  dashboard_slug text not null,
  generated_at timestamptz,
  executed_at timestamptz,
  payload jsonb not null
);

alter table public.dashboard_current enable row level security;
alter table public.dashboard_history enable row level security;

do $$
begin
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'dashboard_current'
      and policyname = 'dashboard_current_select_public'
  ) then
    create policy "dashboard_current_select_public"
    on public.dashboard_current
    for select
    to anon, authenticated
    using (true);
  end if;
end
$$;

do $$
begin
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'dashboard_history'
      and policyname = 'dashboard_history_select_public'
  ) then
    create policy "dashboard_history_select_public"
    on public.dashboard_history
    for select
    to anon, authenticated
    using (true);
  end if;
end
$$;
