variable "telegram_bot_token" {
  type      = string
  sensitive = true
}

variable "admins" {
  type        = list(string)
  description = "Telegram user IDs for all users who can send commands to bot"
  default     = []
}
