/**
 * CardBack - the teacher side of every card type (v3).
 *
 * One component for all 7 types. What differs per type (color, label, which
 * sections appear) lives in lib/cardTypes.ts. Layout, top to bottom:
 *
 *   header   icon + type, ~minutes, ★ CORE
 *   title    English title + Hebrew
 *   goal     objective + the deck's value pill
 *   sections per type: SAY / ASK / Hebrew strip / week / faces / trio / home blocks
 *   footer   transition to the next card + guide page
 *
 * Nothing here hides overflowing text. If a back is too long, it spills
 * visibly so you notice (the export guard in Phase 2 will fail on it).
 */
import React from 'react';
import { Card, Hebrew, LoadedDeck, StandardBack, HomeBack } from '@/types/card';
import { CARD_TYPES, BackSection, backHeaderLabel, weekDayLabel } from '@/lib/cardTypes';
import { parseMarkup } from '@/lib/markup';
import { TypeIcon, TargetIcon, HandIcon, BookIcon, FeelingFace } from './icons';

/** Renders **bold** / [cue] / newline markup. */
function Markup({ text }: { text: string }) {
  return (
    <>
      {parseMarkup(text).map((t, i) => {
        if (t.kind === 'break') return <br key={i} />;
        if (t.kind === 'bold') return <b key={i}>{t.text}</b>;
        if (t.kind === 'cue') return <span key={i} className="cue">{t.text}</span>;
        return <React.Fragment key={i}>{t.text}</React.Fragment>;
      })}
    </>
  );
}

function HebrewStrip({ hebrew, showHand }: { hebrew: Hebrew; showHand: boolean }) {
  return (
    <div className="heb">
      <span className="w">{hebrew.word}</span>
      <span className="t">
        {hebrew.translit && <><b>{hebrew.translit}</b> · </>}&ldquo;{hebrew.meaning}&rdquo;{hebrew.note && ` (${hebrew.note})`}
        {hebrew.gesture && (
          <>
            <br />
            {showHand && <HandIcon />}
            {hebrew.gesture}
          </>
        )}
      </span>
    </div>
  );
}

function Section({ name, card, deck }: { name: BackSection; card: Card; deck: LoadedDeck }) {
  // Fields that only exist on one kind of back
  const std = card.card_type === 'home' ? null : (card.back as StandardBack);
  const home = card.card_type === 'home' ? (card.back as HomeBack) : null;

  switch (name) {
    case 'say':
      return std ? (
        <div className="say">
          <div className="lbl">SAY</div>
          <p><Markup text={std.say} /></p>
        </div>
      ) : null;

    case 'ask':
      return std && std.ask.length > 0 ? (
        <div className="ask">
          <div className="lbl">ASK</div>
          <ul>
            {std.ask.map((q, i) => (
              <li key={i}>
                <span className="mark">{q.type === 'nonverbal' ? <HandIcon /> : '?'}</span>
                {q.text}
              </li>
            ))}
          </ul>
        </div>
      ) : null;

    case 'hebrew':
      return card.back.hebrew ? <HebrewStrip hebrew={card.back.hebrew} showHand={!home} /> : null;

    case 'week':
      return deck.week_plan.length > 0 ? (
        <div>
          <div className="lbl">THIS WEEK</div>
          <div className="week">
            {deck.week_plan.map((d) => (
              <div key={d.day}><b>{weekDayLabel(d.day, deck)}</b>{d.label}</div>
            ))}
          </div>
        </div>
      ) : null;

    case 'faces':
      return std?.faces?.length ? (
        <div className="faces">
          {std.faces.map((f) => (
            <figure key={f}><FeelingFace face={f} />{f}</figure>
          ))}
        </div>
      ) : null;

    case 'trio':
      return std?.trio?.length ? (
        <div className="trio">
          {std.trio.map((t, i) => (
            <div key={i}>
              <span className="big">{t.big}</span>
              {t.line1}<br /><b>{t.line2}</b>
            </div>
          ))}
        </div>
      ) : null;

    case 'shabbat':
      return home ? (
        <div className="say">
          <div className="lbl">AT THE SHABBAT TABLE, ASK</div>
          <div className="bi">
            <div className="en">{home.shabbat_question.en}</div>
            <div className="he2">{home.shabbat_question.he}</div>
          </div>
        </div>
      ) : null;

    case 'try':
      return home && home.try_at_home.length > 0 ? (
        <div className="ask">
          <div className="lbl">TRY AT HOME</div>
          <ul>
            {home.try_at_home.map((t, i) => (
              <li key={i}>
                <span className="mark"><HandIcon /></span>
                {t.text} <i>({t.tag === 'shabbat-friendly' ? 'Shabbat-friendly' : 'before Shabbat'})</i>
              </li>
            ))}
          </ul>
        </div>
      ) : null;
  }
}

export function CardBack({ card, deck }: { card: Card; deck: LoadedDeck }) {
  const type = CARD_TYPES[card.card_type];
  const isHome = card.card_type === 'home';
  const std = isHome ? null : (card.back as StandardBack);

  const headerLabel = backHeaderLabel(card, deck);
  const titleHe = std?.title_he ?? card.title_he;

  return (
    <div className="pp-card" id={`card-${card.card_id}-back`} style={{ '--c': type.color } as React.CSSProperties}>
      <div className="hdr">
        <TypeIcon type={card.card_type} />
        {headerLabel}
        <span className="meta">{std ? `~${std.minutes} min` : 'for families'}</span>
        {std?.core && <span className="core">★ CORE</span>}
      </div>

      <div className="body">
        <div className="title">
          <h3>{card.title_en}</h3>
          <span className="he">{titleHe}</span>
        </div>
        <div className="goal">
          {!isHome && <TargetIcon />}
          <span><Markup text={card.back.objective} /></span>
          <span className="value">{deck.value.en}</span>
        </div>

        {type.sections.map((name) => (
          <Section key={name} name={name} card={card} deck={deck} />
        ))}
        <div className="spacer" />
      </div>

      <div className="ftr">
        <span className="next">{isHome ? card.back.transition : `▸ ${card.back.transition}`}</span>
        {isHome ? (
          <span className="guide">Parasha Pack</span>
        ) : std?.guide_ref ? (
          <span className="guide">
            <BookIcon />
            Guide p.{std.guide_ref.page}
            {std.guide_ref.note && ` · ${std.guide_ref.note}`}
          </span>
        ) : null}
      </div>
    </div>
  );
}
