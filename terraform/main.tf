data "aws_iam_policy_document" "default" {
  statement {
    effect = "Allow"
    actions = [
      "iot:Publish"
    ]
    resources = [
      "*"
    ]
  }
}


module "lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name   = "christmas-lights-telegram-bot"
  handler         = "app.handler"
  runtime         = "python3.12"
  source_path     = "../src/"
  architectures   = ["arm64"]
  build_in_docker = true

  attach_policy_json = true
  policy_json        = data.aws_iam_policy_document.default.json

  cloudwatch_logs_retention_in_days = 1

  create_lambda_function_url = true
  authorization_type         = "NONE"

  environment_variables = {
    LIST_OF_ADMINS     = join(",", var.admins)
    TELEGRAM_BOT_TOKEN = var.telegram_bot_token
  }
}
