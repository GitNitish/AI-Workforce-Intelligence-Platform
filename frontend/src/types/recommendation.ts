export interface RecommendationRequest {
  staffing_requirement_id: string
}

export interface RecommendationItem {
  employee_id: string
  employee_code: string
  employee_name: string
  designation: string | null
  department: string | null
  experience_years: number
  availability_status: string
  utilization_percentage: number
  location: string | null
  status: string
  rank: number
  score: number
  eligibility_status: string
  matched_skills: string[]
  reason: string
}

export interface RecommendationResponse {
  staffing_requirement_id: string
  recommendations: RecommendationItem[]
  generated_at: string
  message: string
}
