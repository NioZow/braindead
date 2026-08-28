{
  config,
  lib,
  pkgs,
  homeDir,
  ...
}: let
  cfg = config.custom.programs.braindead;

  flakeSelf = builtins.getFlake (toString ./.);
  braindeadPkg =
    if cfg.package != null
    then cfg.package
    else flakeSelf.packages.${pkgs.system}.default;

  yamlFormat = pkgs.formats.yaml {};

  configFile = yamlFormat.generate "braindead-config.yml" (
    {
      openai_uri = cfg.settings.openaiUri;
      openai_api_key = cfg.settings.openaiApiKey;
      model = cfg.settings.model;
      notes_triage_location = cfg.settings.notesTriageLocation;
    }
    // (lib.optionalAttrs (cfg.settings.youtubeApiKey != null) {
      youtube_api_key = cfg.settings.youtubeApiKey;
    })
    // (lib.optionalAttrs (cfg.settings.youtubeApiKeyPath != null) {
      youtube_api_key_path = toString cfg.settings.youtubeApiKeyPath;
    })
  );
in {
  options.custom.programs.braindead = {
    enable = lib.mkEnableOption "braindead CLI (articles, videos and books summarizer)";

    package = lib.mkOption {
      type = lib.types.nullOr lib.types.package;
      default = null;
      description = ''The braindead package to install. Defaults to the package built by this repository's flake.'';
    };

    settings = {
      youtubeApiKey = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "YouTube Data API key. Mutually exclusive with youtubeApiKeyPath.";
      };

      youtubeApiKeyPath = lib.mkOption {
        type = lib.types.nullOr lib.types.path;
        default = null;
        description = "Path to a file containing the YouTube Data API key. Used instead of youtubeApiKey.";
      };

      openaiUri = lib.mkOption {
        type = lib.types.str;
        default = "http://litellm-proxy:27740";
        description = "Base URL of the OpenAI-compatible API server.";
      };

      openaiApiKey = lib.mkOption {
        type = lib.types.str;
        default = "dummy";
        description = "API key for the OpenAI-compatible server.";
      };

      model = lib.mkOption {
        type = lib.types.str;
        default = "gemini/gemini-3.1-flash-lite-preview";
        description = "Model used for summarization.";
      };

      notesTriageLocation = lib.mkOption {
        type = lib.types.path;
        default = "~/notes/triage/";
        description = "Directory where generated notes are saved.";
      };
    };
  };

  config = lib.mkIf cfg.enable {
    home.packages = [braindeadPkg];
    home.file.".config/braindead/config.yml".source = configFile;
  };
}