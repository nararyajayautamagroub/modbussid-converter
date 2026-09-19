from __future__ import annotations

import json
import zipfile
from pathlib import Path

from .light_animation import build_animation, to_dict


def _lua_script(light_type: str) -> str:
    animation = to_dict(build_animation(light_type))
    frames = animation["frames"]
    lua_frames = ",\n".join(
        "    {time=%.4f, intensity=%.4f, enabled=%s, phase=%.1f}"
        % (
            frame["time"],
            frame["intensity"],
            "true" if frame["enabled"] else "false",
            frame["phase"],
        )
        for frame in frames
    )

    return f"""-- Game Mod Asset Lab
-- Roblox Studio installer/preview for {light_type}.
-- Generated from game-mod-light-animation-v1.
local TweenService = game:GetService("TweenService")

local model = Instance.new("Model")
model.Name = "GameModAssetLab_{light_type}"
model.Parent = workspace

local holder = Instance.new("Part")
holder.Name = "AnimatedLight"
holder.Anchored = true
holder.CanCollide = false
holder.Material = Enum.Material.Neon
holder.Size = Vector3.new(0.5, 0.5, 0.5)
holder.Position = Vector3.new(0, 3, 0)
holder.Parent = model

local light = Instance.new("PointLight")
light.Name = "GameModLight"
light.Brightness = 0
light.Range = 20
light.Enabled = false
light.Parent = holder

local frames = {{
{lua_frames}
}}

local function applyFrame(frame)
    light.Enabled = frame.enabled
    light.Brightness = frame.intensity * 8

    if "{light_type}" == "rotator" then
        holder.Orientation = Vector3.new(0, frame.phase, 0)
    end
end

while model.Parent do
    for index, frame in ipairs(frames) do
        applyFrame(frame)
        local nextFrame = frames[index + 1] or frames[1]
        local duration = nextFrame.time - frame.time
        if duration <= 0 then
            duration = 0.05
        end
        task.wait(duration)
    end
end
"""


def export_light_package(light_type: str, target: Path, platform: str) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    animation = to_dict(build_animation(light_type))
    payload = {
        "platform": platform,
        "asset_type": "light_animation",
        "animation": animation,
    }

    json_path = target.with_suffix(".json")
    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    zip_path = target.with_suffix(".zip")
    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        archive.write(json_path, json_path.name)
        if platform == "roblox":
            lua_path = target.with_name(f"{target.name}_studio.lua")
            lua_path.write_text(_lua_script(light_type), encoding="utf-8")
            archive.write(lua_path, lua_path.name)

    return zip_path
