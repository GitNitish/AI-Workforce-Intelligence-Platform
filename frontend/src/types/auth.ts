export interface CurrentUser {
  user_id: string
  username: string
  email: string
  role: string | null
  status: string
  permissions: string[]
}

export interface LoginResponse {
  access_token: string
  token_type: string
}