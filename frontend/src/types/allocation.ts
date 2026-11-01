export interface Allocation {
  allocation_id: string
  employee_id: string
  project_id: string
  staffing_requirement_id: string | null
  allocation_percentage: number
  start_date: string
  end_date: string | null
  status: string
  allocated_by: string | null
  created_at: string
  updated_at: string
}