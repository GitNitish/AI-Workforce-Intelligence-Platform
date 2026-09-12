import { useState } from 'react'
import type {
  RecommendationResponse,
  RecommendationItem,
} from '../types/recommendation'
import { generateRecommendations } from '../services/recommendations'

const VERIFIED_STAFFING_REQUIREMENT_ID =
  '5d3a37fc-cccf-4e24-bae2-d2fb6c175e23'

function RecommendationsPage() {
  const [staffingRequirementId, setStaffingRequirementId] = useState(
    VERIFIED_STAFFING_REQUIREMENT_ID,
  )
  const [result, setResult] = useState<RecommendationResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleGenerateRecommendations() {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await generateRecommendations({
        staffing_requirement_id: staffingRequirementId.trim(),
      })

      setResult(response)
    } catch (requestError) {
      const message =
        requestError instanceof Error
          ? requestError.message
          : 'Unable to generate recommendations.'

      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="page">
      <div className="page-header">
        <h2>Recommendations</h2>
        <p>
          Generate AI-powered workforce recommendations for a staffing
          requirement.
        </p>
      </div>

      <div className="recommendation-form">
        <label htmlFor="staffing-requirement-id">
          Staffing Requirement ID
        </label>

        <input
          id="staffing-requirement-id"
          type="text"
          value={staffingRequirementId}
          onChange={(event) => setStaffingRequirementId(event.target.value)}
          placeholder="Enter staffing requirement ID"
        />

        <button
          type="button"
          onClick={handleGenerateRecommendations}
          disabled={loading || !staffingRequirementId.trim()}
        >
          {loading ? 'Generating...' : 'Generate Recommendations'}
        </button>
      </div>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      {result && (
        <div className="recommendation-results">
          <div className="results-summary">
            <div>
              <span>Requirement</span>
              <strong>{result.staffing_requirement_id}</strong>
            </div>

            <div>
              <span>Recommendations</span>
              <strong>{result.recommendations.length}</strong>
            </div>

            <div>
              <span>Status</span>
              <strong>{result.message ?? 'Generated successfully'}</strong>
            </div>
          </div>

          <div className="recommendation-list">
            {result.recommendations.map(
              (recommendation: RecommendationItem) => (
                <article
                  className="recommendation-card"
                  key={recommendation.employee_id}
                >
                  <div className="recommendation-rank">
                    #{recommendation.rank}
                  </div>

                  <div className="recommendation-content">
                    <div className="recommendation-title">
                      <h3>{recommendation.employee_id}</h3>
                      <span className="recommendation-score">
                        Score: {recommendation.score}
                      </span>
                    </div>

                    <p>
                      <strong>Eligibility:</strong>{' '}
                      {recommendation.eligibility_status}
                    </p>

                    <p>
                      <strong>Matched skills:</strong>{' '}
                      {recommendation.matched_skills.length > 0
                        ? recommendation.matched_skills.join(', ')
                        : 'None'}
                    </p>

                    <p>
                      <strong>Reason:</strong> {recommendation.reason}
                    </p>
                  </div>
                </article>
              ),
            )}
          </div>
        </div>
      )}
    </section>
  )
}

export default RecommendationsPage