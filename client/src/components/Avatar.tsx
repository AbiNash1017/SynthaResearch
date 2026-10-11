"use client";

import React, { useState } from "react";

/**
 * Curated soft pastel palette matching SynthaResearch's moss / sage visual language.
 */
export const AVATAR_PASTEL_PALETTE = [
  "b6e3f4",
  "c0aede",
  "d1d4f9",
  "ffd5dc",
  "ffdfbf",
  "d8f3dc",
  "e7f5dc",
  "faedcd",
];

export const MALE_HEADS = [
  "short1",
  "short2",
  "short3",
  "short4",
  "short5",
  "flatTop",
  "flatTopLong",
  "pomp",
  "shaved1",
  "shaved2",
  "shaved3",
  "noHair1",
  "noHair2",
  "noHair3",
  "mohawk",
  "mohawk2",
  "hatBeanie",
  "hatHip",
  "grayShort",
  "dreads1",
  "dreads2",
  "afro",
];

export const FEMALE_HEADS = [
  "bun",
  "bun2",
  "buns",
  "grayBun",
  "long",
  "longCurly",
  "longBangs",
  "longAfro",
  "bangs",
  "bangs2",
  "bantuKnots",
  "medium1",
  "medium2",
  "medium3",
  "mediumBangs",
  "mediumBangs2",
  "mediumBangs3",
  "mediumStraight",
  "hijab",
  "twists",
  "twists2",
];

export const MALE_AVATAR_PRESETS = [
  { id: "m1", seed: "Marcus Vance", label: "Marcus" },
  { id: "m2", seed: "Julian Rossi", label: "Julian" },
  { id: "m3", seed: "Andre Washington", label: "Andre" },
  { id: "m4", seed: "Leo Hunter", label: "Leo" },
  { id: "m5", seed: "David Chen", label: "David" },
  { id: "m6", seed: "Kai Takahashi", label: "Kai" },
  { id: "m7", seed: "Ethan Scott", label: "Ethan" },
  { id: "m8", seed: "Lucas Meyer", label: "Lucas" },
];

export const FEMALE_AVATAR_PRESETS = [
  { id: "f1", seed: "Mei-Ling Wu", label: "Mei-Ling" },
  { id: "f2", seed: "Nadia Chernova", label: "Nadia" },
  { id: "f3", seed: "Elena Rostova", label: "Elena" },
  { id: "f4", seed: "Sophia Taylor", label: "Sophia" },
  { id: "f5", seed: "Amina Diallo", label: "Amina" },
  { id: "f6", seed: "Chloe Bennett", label: "Chloe" },
  { id: "f7", seed: "Sarah Jenkins", label: "Sarah" },
  { id: "f8", seed: "Zara Al-Mansoor", label: "Zara" },
];

/**
 * Normalizes input gender string into 'male' | 'female' | null.
 */
export function normalizeGender(gender?: string | null): "male" | "female" | null {
  if (!gender) return null;
  const g = gender.trim().toLowerCase();
  if (
    g.startsWith("fe") ||
    g.includes("woman") ||
    g.includes("female") ||
    g === "f" ||
    g === "girl"
  ) {
    return "female";
  }
  if (
    g.includes("male") ||
    g.includes("man") ||
    g === "m" ||
    g === "boy"
  ) {
    return "male";
  }
  return null;
}

export interface AvatarUrlOptions {
  gender?: string | null;
  palette?: string[];
  head?: string[];
  facialHairProbability?: number;
}

/**
 * Builds a deterministic DiceBear Open Peeps illustration URL for a given seed and gender.
 */
export function getOpenPeepsAvatarUrl(
  seed?: string | null,
  options?: AvatarUrlOptions
): string {
  const safeSeed = encodeURIComponent((seed && seed.trim()) || "Persona");
  const palette = options?.palette || AVATAR_PASTEL_PALETTE;
  const bg = palette.join(",");
  const params = new URLSearchParams({
    seed: safeSeed,
    backgroundColor: bg,
    maskProbability: "0",
  });

  const normGender = normalizeGender(options?.gender);

  if (options?.head && options.head.length > 0) {
    params.set("head", options.head.join(","));
  } else if (normGender === "male") {
    params.set("head", MALE_HEADS.join(","));
    const fhp =
      options?.facialHairProbability !== undefined
        ? options.facialHairProbability
        : 30;
    params.set("facialHairProbability", fhp.toString());
  } else if (normGender === "female") {
    params.set("head", FEMALE_HEADS.join(","));
    params.set("facialHairProbability", "0");
  }

  return `https://api.dicebear.com/9.x/open-peeps/svg?${params.toString()}`;
}

export interface AvatarProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  seed?: string | null;
  gender?: string | null;
  alt?: string;
  fallbackText?: string;
  fallbackIcon?: React.ReactNode;
  palette?: string[];
  head?: string[];
  facialHairProbability?: number;
}

export function Avatar({
  seed,
  gender,
  alt = "Avatar",
  className = "w-8 h-8 rounded-xl",
  fallbackText,
  fallbackIcon,
  palette,
  head,
  facialHairProbability,
  ...rest
}: AvatarProps) {
  const [hasError, setHasError] = useState(false);
  const avatarUrl = getOpenPeepsAvatarUrl(seed, {
    gender,
    palette,
    head,
    facialHairProbability,
  });

  if (hasError || !seed) {
    const initial = fallbackText
      ? fallbackText.slice(0, 2).toUpperCase()
      : seed
      ? seed.trim().slice(0, 1).toUpperCase()
      : "U";

    return (
      <div
        className={`flex items-center justify-center font-bold text-xs uppercase shrink-0 bg-[#465135] text-[#CFE1B9] border border-[#CFE1B9]/60 shadow-xs ${className}`}
        title={alt}
      >
        {fallbackIcon || initial}
      </div>
    );
  }

  return (
    <img
      src={avatarUrl}
      alt={alt}
      loading="lazy"
      decoding="async"
      onError={() => setHasError(true)}
      className={`object-cover shrink-0 select-none border border-[#CFE1B9]/60 shadow-2xs ${className}`}
      {...rest}
    />
  );
}

export default Avatar;
