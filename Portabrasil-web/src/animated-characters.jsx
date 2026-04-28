"use client";

import { useState, useEffect, useRef } from "react";

const VB = { w: 400, h: 400 };

/** 眼白 + 瞳孔（或闭眼横线）；坐标为 SVG viewBox 单位 */
function SvgEye({
  cx,
  cy,
  hasWhite = true,
  mousePos,
  blinkProgress = 0,
  forceX,
  forceY,
  isClosed = false,
  maxOffset = 4,
  rWhite = 7,
  rPupil = 2.5,
}) {
  const blinkScale = 1 - blinkProgress * 0.95;
  const offX = isClosed ? 0 : forceX !== undefined ? forceX : mousePos.x * maxOffset;
  const offY = isClosed ? 0 : forceY !== undefined ? forceY : mousePos.y * maxOffset;

  return (
    <g transform={`translate(${cx},${cy})`}>
      <g transform={`scale(1,${blinkScale})`}>
        {isClosed ? (
          <line x1="-5" y1="0" x2="5" y2="0" stroke="#111" strokeWidth="2.5" strokeLinecap="round" />
        ) : hasWhite ? (
          <>
            <circle cx="0" cy="0" r={rWhite} fill="#ffffff" />
            <circle cx={offX} cy={offY} r={rPupil} fill="#111111" />
          </>
        ) : (
          <circle cx={offX} cy={offY} r="3.5" fill="#111111" />
        )}
      </g>
    </g>
  );
}

/** 绕一点做 skewX（度），等价 transform-origin: bottom center */
function skewAt(x, y, skewDeg, children) {
  return (
    <g transform={`translate(${x},${y}) skewX(${skewDeg}) translate(${-x},${-y})`}>
      {children}
    </g>
  );
}

export function AnimatedCharacters({ isTyping = false, showPassword = false, passwordLength = 0 }) {
  const purpleRef = useRef(null);
  const blackRef = useRef(null);
  const orangeRef = useRef(null);
  const yellowRef = useRef(null);
  const sceneRef = useRef(null);

  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isLookingAtEachOther, setIsLookingAtEachOther] = useState(false);
  const [isPurplePeeking, setIsPurplePeeking] = useState(false);
  const [blinkProgress, setBlinkProgress] = useState(0);
  const [purpleRectProgress, setPurpleRectProgress] = useState(0);

  const [pointer, setPointer] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setPointer({ x: e.clientX, y: e.clientY });
      if (!sceneRef.current) return;
      const rect = sceneRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const dx = e.clientX - centerX;
      const dy = e.clientY - centerY;
      const distance = Math.min(1, Math.sqrt(dx * dx + dy * dy) / 400);
      const angle = Math.atan2(dy, dx);
      setMousePos({
        x: Math.cos(angle) * distance,
        y: Math.sin(angle) * distance,
      });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  // showPassword 切换时重置眨眼，让眼睛保持完全睁开状态过渡，避免半闭状态闪烁
  useEffect(() => {
    setBlinkProgress(0);
  }, [showPassword]);

  useEffect(() => {
    let blinkTimer;
    let blinkStart = null;
    const blinkDuration = 150;

    const animateBlink = (timestamp) => {
      if (!blinkStart) blinkStart = timestamp;
      const elapsed = timestamp - blinkStart;

      if (elapsed < blinkDuration * 0.4) {
        const progress = elapsed / (blinkDuration * 0.4);
        setBlinkProgress(Math.sin((progress * Math.PI) / 2));
      } else if (elapsed < blinkDuration) {
        const progress = (elapsed - blinkDuration * 0.4) / (blinkDuration * 0.6);
        setBlinkProgress(1 - Math.pow(progress, 0.5));
      } else {
        setBlinkProgress(0);
        blinkTimer = setTimeout(() => {
          blinkStart = null;
          requestAnimationFrame(animateBlink);
        }, Math.random() * 3000 + 2000);
        return;
      }
      requestAnimationFrame(animateBlink);
    };

    blinkTimer = setTimeout(() => {
      requestAnimationFrame(animateBlink);
    }, Math.random() * 2000);

    return () => clearTimeout(blinkTimer);
  }, []);

  useEffect(() => {
    let rafId;
    let start = null;
    const DURATION = 450; // 稍微延长，让 peek/shrink 更平滑
    const target = showPassword ? 1 : 0;
    const fromVal = purpleRectProgress;

    const animate = (ts) => {
      if (!start) start = ts;
      const t = Math.min(1, (ts - start) / DURATION);
      const eased = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
      // 正确的 lerp: 从 fromVal 插值到 target
      setPurpleRectProgress(fromVal + (target - fromVal) * eased);
      if (t < 1) rafId = requestAnimationFrame(animate);
    };
    rafId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafId);
  }, [showPassword]);

  useEffect(() => {
    if (isTyping) {
      setIsLookingAtEachOther(true);
      const timer = setTimeout(() => setIsLookingAtEachOther(false), 600);
      return () => clearTimeout(timer);
    }
    setIsLookingAtEachOther(false);
  }, [isTyping]);

  useEffect(() => {
    if (passwordLength > 0 && showPassword) {
      const schedulePeek = () => {
        const t = setTimeout(() => {
          setIsPurplePeeking(true);
          setTimeout(() => {
            setIsPurplePeeking(false);
            schedulePeek();
          }, 600 + Math.random() * 400);
        }, Math.random() * 4000 + 3000);
        return t;
      };
      const t = schedulePeek();
      return () => clearTimeout(t);
    }
    setIsPurplePeeking(false);
  }, [passwordLength, showPassword]);

  const calculatePosition = (ref, intensity = 1) => {
    if (!ref.current) return { faceX: 0, faceY: 0, bodySkew: 0 };
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 3;
    const deltaX = pointer.x - centerX;
    const deltaY = pointer.y - centerY;
    const faceX = Math.max(-10, Math.min(10, (deltaX / 30) * intensity));
    const faceY = Math.max(-6, Math.min(6, (deltaY / 40) * intensity));
    const bodySkew = Math.max(-5, Math.min(5, -(deltaX / 90) * intensity));
    return { faceX, faceY, bodySkew };
  };

  const purplePos = calculatePosition(purpleRef);
  const blackPos = calculatePosition(blackRef);
  const orangePos = calculatePosition(orangeRef, 1);
  const yellowPos = calculatePosition(yellowRef, 0.65);

  const peek = passwordLength > 0 && showPassword;
  const isHidingPassword = passwordLength > 0 && !showPassword;

  /**
   * 显示密码：身体不倾斜；视线避开（参考图）
   * 紫/黑大眼：瞳孔移到眼白左上；橙/黄小点：尽量朝左
   */
  const bigPeekX = peek ? -3.8 : undefined;
  const bigPeekY = peek ? -3.4 : undefined;
  const dotPeekX = peek ? -2.9 : undefined;
  const dotPeekY = peek ? -0.5 : undefined;

  const pPeek = peek ? { dx: -6, dy: -5 } : { dx: 0, dy: 0 };
  const bPeek = peek ? { dx: -5, dy: -4 } : { dx: 0, dy: 0 };
  const oPeek = peek ? { dx: -9, dy: -1 } : { dx: 0, dy: 0 };
  const yPeek = peek ? { dx: -7, dy: -2 } : { dx: 0, dy: 0 };

  return (
    <div ref={sceneRef} className="absolute inset-0 flex items-center justify-center">
      <svg
        viewBox={`0 0 ${VB.w} ${VB.h}`}
        className="h-full w-full max-h-[min(72vh,520px)] overflow-visible"
        preserveAspectRatio="xMidYMid meet"
        aria-hidden
      >
        <g transform="scale(1.12) translate(-20 -40)">
        {/* 后：紫色圆角矩形 → peek 时右侧向内收，左边固定不动，呈现"背过身"的视效 */}
        <g ref={purpleRef}>
          {skewAt(185, 350, 0, (
            <g>
              {/* 紫色身体主体 */}
              <rect
                x="130"
                y="65"
                width="118"
                height="240"
                rx="10"
                fill="#6F32FF"
              />

              <SvgEye
                cx={189 + purplePos.faceX * 0.35 + pPeek.dx}
                cy={120 + purplePos.faceY * 0.35 + pPeek.dy}
                hasWhite
                mousePos={mousePos}
                blinkProgress={blinkProgress}
                forceX={bigPeekX}
                forceY={bigPeekY}
                maxOffset={4}
              />
              <SvgEye
                cx={228 + purplePos.faceX * 0.35 + pPeek.dx}
                cy={120 + purplePos.faceY * 0.35 + pPeek.dy}
                hasWhite
                mousePos={mousePos}
                blinkProgress={blinkProgress}
                forceX={bigPeekX}
                forceY={bigPeekY}
                maxOffset={4}
              />
            </g>
          ))}
        </g>

        {/* 中：黑色圆角竖条 */}
        <g ref={blackRef}>
          {skewAt(235, 350, 0, (
            <>
              <rect x="200" y="150" width="70" height="200" rx="12" fill="#22242A" />
              <SvgEye
                cx={220 + blackPos.faceX * 0.35 + bPeek.dx}
                cy={175 + blackPos.faceY * 0.35 + bPeek.dy}
                hasWhite
                mousePos={mousePos}
                blinkProgress={blinkProgress}
                forceX={bigPeekX}
                forceY={bigPeekY}
                rWhite={6}
                rPupil={2.2}
                maxOffset={3.5}
              />
              <SvgEye
                cx={245 + blackPos.faceX * 0.35 + bPeek.dx}
                cy={175 + blackPos.faceY * 0.35 + bPeek.dy}
                hasWhite
                mousePos={mousePos}
                blinkProgress={blinkProgress}
                forceX={bigPeekX}
                forceY={bigPeekY}
                rWhite={6}
                rPupil={2.2}
                maxOffset={3.5}
              />
            </>
          ))}
        </g>

        {/* 前左：橙色半圆顶 */}
        <g ref={orangeRef}>
          {skewAt(140, 350, 0, (
            <>
              <path d="M 60 350 A 80 80 0 0 1 220 350 Z" fill="#FF9B6A" />
              <SvgEye
                cx={115 + orangePos.faceX * 0.3 + oPeek.dx}
                cy={290 + orangePos.faceY * 0.3 + oPeek.dy}
                hasWhite={false}
                mousePos={mousePos}
                blinkProgress={0}
                forceX={dotPeekX}
                forceY={dotPeekY}
                maxOffset={5}
              />
              <SvgEye
                cx={145 + orangePos.faceX * 0.3 + oPeek.dx}
                cy={290 + orangePos.faceY * 0.3 + oPeek.dy}
                hasWhite={false}
                mousePos={mousePos}
                blinkProgress={0}
                forceX={dotPeekX}
                forceY={dotPeekY}
                maxOffset={5}
              />
            </>
          ))}
        </g>

        {/* 前右：黄色拱门 */}
        <g ref={yellowRef}>
          {skewAt(290, 350, 0, (
            <>
              <path d="M 240 260 A 50 50 0 0 1 340 260 L 340 350 L 240 350 Z" fill="#EEDB56" />
              <SvgEye
                cx={275 + yellowPos.faceX * 0.3 + yPeek.dx}
                cy={260 + yellowPos.faceY * 0.3 + yPeek.dy}
                hasWhite={false}
                mousePos={mousePos}
                blinkProgress={0}
                forceX={dotPeekX}
                forceY={dotPeekY}
                maxOffset={3}
              />
              <SvgEye
                cx={305 + yellowPos.faceX * 0.3 + yPeek.dx}
                cy={260 + yellowPos.faceY * 0.3 + yPeek.dy}
                hasWhite={false}
                mousePos={mousePos}
                blinkProgress={0}
                forceX={dotPeekX}
                forceY={dotPeekY}
                maxOffset={3}
              />
              <line
                x1={268 + yellowPos.faceX * 0.4 + yPeek.dx}
                y1="295"
                x2={312 + yellowPos.faceX * 0.4 + yPeek.dx}
                y2="295"
                stroke="#111"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
            </>
          ))}
        </g>
        </g>
      </svg>
    </div>
  );
}
