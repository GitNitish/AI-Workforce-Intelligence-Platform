import type {
  RecommendationRequest,
  RecommendationResponse,
} from '../types/recommendation'
import { apiRequest } from './api'

export async function generateRecommendations(
  request: RecommendationRequest,
): Promise<RecommendationResponse> {
  return apiRequest<RecommendationResponse>('/recommendations', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}