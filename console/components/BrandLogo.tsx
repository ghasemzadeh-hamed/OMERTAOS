import Image from "next/image";

type BrandLogoProps = {
  className?: string;
  priority?: boolean;
  size?: number;
};

export default function BrandLogo({
  className = "",
  priority = false,
  size = 48,
}: BrandLogoProps) {
  return (
    <Image
      src="/brand/omertaos-logo.png"
      alt="OMERTAOS logo"
      width={size}
      height={size}
      sizes={`${size}px`}
      priority={priority}
      className={`rounded-full object-cover ${className}`}
    />
  );
}
