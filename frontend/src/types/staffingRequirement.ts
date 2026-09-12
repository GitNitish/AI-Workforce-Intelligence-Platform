export interface StaffingRequirement {
  staffing_requirement_id: string
  project_id: string
  role_name: string
  required_quantity: number
  required_experience: number
  required_proficiency: string | null
  start_date: string | null
  end_date: string | null
  priority: string
  status: string
  required_skill_ids: string[]
  required_certifications: string[]
  created_at: string
  updated_at: string
}