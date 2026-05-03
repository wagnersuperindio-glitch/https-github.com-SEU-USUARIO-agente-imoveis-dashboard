drop policy if exists "dashboard_current_select_public" on public.dashboard_current;
drop policy if exists "dashboard_history_select_public" on public.dashboard_history;
drop policy if exists "dashboard_current_select_authenticated" on public.dashboard_current;
drop policy if exists "dashboard_history_select_authenticated" on public.dashboard_history;

create policy "dashboard_current_select_authenticated"
on public.dashboard_current
for select
to authenticated
using (true);

create policy "dashboard_history_select_authenticated"
on public.dashboard_history
for select
to authenticated
using (true);
