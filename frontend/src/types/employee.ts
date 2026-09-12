export interface Employee {
  employee_id: string
  employee_code: string
  name: string
  email: string
  designation: string | null
  department: string | null
  experience_years: number
  availability_status: string
  utilization_percentage: number
  location: string | null
  status: string
  created_at: string
  updated_at: string
}