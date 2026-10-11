"use client";

import React, { useState } from "react";
import {
  Avatar,
  MALE_AVATAR_PRESETS,
  FEMALE_AVATAR_PRESETS,
} from "./Avatar";
import { RefreshCw, Check } from "lucide-react";

interface AvatarPickerProps {
  selectedSeed: string;
  selectedGender: "male" | "female";
  onSelect: (seed: string, gender: "male" | "female") => void;
  className?: string;
}

export function AvatarPicker({
  selectedSeed,
  selectedGender,
  onSelect,
  className = "",
}: AvatarPickerProps) {
  const [gender, setGender] = useState<"male" | "female">(selectedGender);
  const [customCounter, setCustomCounter] = useState(1);

  const presets =
    gender === "male" ? MALE_AVATAR_PRESETS : FEMALE_AVATAR_PRESETS;

  const handleGenderSwitch = (newGender: "male" | "female") => {
    setGender(newGender);
    const newPresets =
      newGender === "male" ? MALE_AVATAR_PRESETS : FEMALE_AVATAR_PRESETS;
    onSelect(newPresets[0].seed, newGender);
  };

  const handleShuffle = () => {
    const nextCount = customCounter + 1;
    setCustomCounter(nextCount);
    const randomSeed = `${gender === "male" ? "Persona_M" : "Persona_F"}_${Date.now().toString().slice(-4)}_${nextCount}`;
    onSelect(randomSeed, gender);
  };

  return (
    <div className={`space-y-3.5 ${className}`}>
      {/* Gender Selector Tabs */}
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-[#465135] uppercase tracking-wider block">
          Choose Profile Avatar
        </label>
        <div className="flex p-0.5 rounded-xl bg-[#F4F7F4] border border-[#CFE1B9]">
          <button
            type="button"
            onClick={() => handleGenderSwitch("male")}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              gender === "male"
                ? "bg-[#465135] text-white shadow-2xs"
                : "text-[#5B6845] hover:text-[#2D3522]"
            }`}
          >
            Male
          </button>
          <button
            type="button"
            onClick={() => handleGenderSwitch("female")}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              gender === "female"
                ? "bg-[#465135] text-white shadow-2xs"
                : "text-[#5B6845] hover:text-[#2D3522]"
            }`}
          >
            Female
          </button>
        </div>
      </div>

      {/* Preset Avatars Grid */}
      <div className="grid grid-cols-4 sm:grid-cols-4 gap-2">
        {presets.slice(0, 8).map((p) => {
          const isSelected = selectedSeed === p.seed;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => onSelect(p.seed, gender)}
              className={`relative p-1.5 rounded-2xl flex flex-col items-center gap-1 transition-all border cursor-pointer ${
                isSelected
                  ? "bg-[#E7F5DC] border-[#728156] ring-2 ring-[#728156]/40 shadow-xs"
                  : "bg-white border-[#CFE1B9]/70 hover:bg-[#F8FAF7] hover:border-[#728156]/60"
              }`}
            >
              <div className="relative">
                <Avatar
                  seed={p.seed}
                  gender={gender}
                  alt={p.label}
                  className="w-11 h-11 rounded-xl"
                />
                {isSelected && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#728156] text-white flex items-center justify-center shadow-xs">
                    <Check className="w-2.5 h-2.5 stroke-[3]" />
                  </div>
                )}
              </div>
              <span className="text-[10px] font-medium text-[#465135] truncate max-w-full">
                {p.label}
              </span>
            </button>
          );
        })}
      </div>

      {/* Shuffle Button & Live Preview Strip */}
      <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#F8FAF7] border border-[#CFE1B9]/60">
        <div className="flex items-center gap-2.5 min-w-0">
          <Avatar
            seed={selectedSeed}
            gender={gender}
            alt="Selected Avatar Preview"
            className="w-8 h-8 rounded-lg shrink-0 shadow-2xs"
          />
          <div className="min-w-0">
            <span className="text-[10px] text-[#728156] font-medium block">
              Active Avatar
            </span>
            <p className="text-xs font-bold text-[#2D3522] truncate">
              {selectedSeed} ({gender})
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleShuffle}
          className="px-2.5 py-1 rounded-lg bg-white border border-[#CFE1B9] text-[#5B6845] hover:text-[#2D3522] hover:bg-[#E7F5DC] text-[11px] font-semibold flex items-center gap-1.5 transition-all shadow-2xs cursor-pointer shrink-0"
          title="Generate a random unique look"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Shuffle</span>
        </button>
      </div>
    </div>
  );
}

export default AvatarPicker;
