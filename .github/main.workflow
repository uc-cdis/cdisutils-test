workflow "Run python formatter" {
  on = "pull_request"
  resolves = ["Run wool"]
}

action "Run wool" {
  uses = "uc-cdis/wool@feat/workflow"
  secrets = ["GITHUB_TOKEN"]
}
