import type { LinksFunction } from "@remix-run/node";
import type { Caption } from "../client/models/Caption";
import styles from "./ClipList.css";

export type range = [Caption, Caption] | [Caption] | undefined;
function addLeadingZero(n: number, fixedPrecision = 0): string {
  if (n === 0) return "00";

  if (n < 10) return `0${n.toFixed(fixedPrecision)}`;

  return n.toFixed(fixedPrecision);
}

function formatTime(time: number): string {
  const seconds = time % 60;
  const minutes = ((time - seconds) / 60) % 60;
  const hours = (time - seconds - 60 * minutes) / 60;
  return `${hours}:${addLeadingZero(minutes)}:${addLeadingZero(seconds, 2)}`;
}

export const links: LinksFunction = () => {
  return [{ rel: "stylesheet", href: styles }];
};

interface IProps {
  captions: Caption[];
  selectedRange: range;
  setSelectedRange: (foo: Caption) => void;
}

const checkIfInRange = (
  r: [number, number] | number | undefined,
  value: number
): boolean =>
  r && r.length === 2 ? value >= r[0] && value <= r[1] : value === r[0];

export function ClipList(props: IProps) {
  const { captions, selectedRange, setSelectedRange } = props;

  return (
    <div className="clip-list">
      {captions.map((caption) => {
        const isSelected =
          selectedRange &&
          checkIfInRange(
            selectedRange.map((c) => c.order) as [number, number],
            caption.order
          );
        return (
          <div
            key={caption.id}
            className="clip-entry"
            onClick={() => setSelectedRange(caption)}
            id={caption.id}
            style={{ flex: caption.stop - caption.start }}
          >
            <div className="clip-list-time">
              <i>{formatTime((caption.start + caption.stop) / 2)}</i>
            </div>
            <div
              className={`clip-separator ${isSelected && "clip-selected"}`}
            />
            <div className="clip-list-text">
              <span
                dangerouslySetInnerHTML={{
                  __html: caption.text,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
