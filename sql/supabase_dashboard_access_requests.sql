create table if not exists public.dashboard_access_requests (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  reviewed_at timestamptz,
  reviewed_by text,
  status text not null default 'pendente',
  full_name text not null,
  email text not null,
  cpf text not null,
  document_type text not null,
  document_number text not null,
  phone text not null,
  company_name text not null,
  role_requested text not null,
  justification text
);

alter table public.dashboard_access_requests enable row level security;

drop policy if exists "dashboard_access_requests_insert_open" on public.dashboard_access_requests;
drop policy if exists "dashboard_access_requests_select_admin" on public.dashboard_access_requests;
drop policy if exists "dashboard_access_requests_update_admin" on public.dashboard_access_requests;

create policy "dashboard_access_requests_insert_open"
on public.dashboard_access_requests
for insert
to anon, authenticated
with check (
  status = 'pendente'
  and length(trim(full_name)) > 0
  and length(trim(email)) > 0
  and length(trim(cpf)) = 11
  and length(trim(document_type)) > 0
  and length(trim(document_number)) > 0
  and length(trim(phone)) > 0
  and length(trim(company_name)) > 0
  and length(trim(role_requested)) > 0
);

create policy "dashboard_access_requests_select_admin"
on public.dashboard_access_requests
for select
to authenticated
using (
  coalesce(auth.jwt() -> 'user_metadata' ->> 'role', '') in ('admin', 'diretoria')
);

create policy "dashboard_access_requests_update_admin"
on public.dashboard_access_requests
for update
to authenticated
using (
  coalesce(auth.jwt() -> 'user_metadata' ->> 'role', '') in ('admin', 'diretoria')
)
with check (
  coalesce(auth.jwt() -> 'user_metadata' ->> 'role', '') in ('admin', 'diretoria')
);
