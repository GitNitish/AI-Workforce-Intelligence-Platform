export interface Project {
  project_id: string
  project_code: string
  project_name: string
  client_name: string | null
  description: string | null
  start_date: string | null
  end_date: string | null
  status: string
  priority: string
  created_at: string
  updated_at: string
}