"use client";
import GuidedIntroManager from "@/components/GuidedIntro/GuidedIntroManager";
import ProfileSelection from "@/components/ProfileSelection.jsx/ProfileSelection";
import { Logo } from "@leafygreen-ui/logo";

export default function Home() {

  return (
    <main className="flex flex-col min-h-screen items-center justify-center relative">
      <div className="absolute top-6 left-6 flex items-center gap-2">
        <Logo height={30} color='green-dark-2' />
      </div>
      <GuidedIntroManager />
      <ProfileSelection/>
    </main>
  );
}
