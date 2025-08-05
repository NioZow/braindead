alias bl = uvx brainless
alias brainless = uvx brainless
def --wrapped 'bl watch' [...args:string] { brainless watch ...$args | from json }
def --wrapped 'bl sync' [...args:string] { brainless sync ...$args | from json }
def --wrapped 'bl videos' [...args:string] { brainless videos ...$args | from json }
def --wrapped 'bl playlists' [...args:string] { brainless playlists ...$args | from json }
def --wrapped 'bl channels' [...args:string] { brainless channels ...$args | from json }


