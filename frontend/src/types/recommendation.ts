export interface RecommendationRequest {
  staffing_requirement_id: string
}

export interface RecommendationItem {
  employee_id: string
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
  message: string | null
}