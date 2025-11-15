import LogoIconV2 from "../assets/logo-icon-v2.svg";
import LogoIcon from "../assets/logo-icon.svg";
import MenuIcon from "../assets/menu.svg";
import TodoistIcon from "../assets/todoist.svg";
import TelegramIcon from "../assets/telegram.svg";

export const enum IconTypes {
  LOGO_OUTLINED,
  MENU_OUTLINED,
  LOGO_OUTLINED_V2,
  TODOIST_OUTLINED,
  TELEGRAM_OUTLINED,
}

export type IconDictionaryType = {
  [key in IconTypes]: React.FunctionComponent<React.SVGAttributes<SVGElement>>;
};

export const IconDictionary: IconDictionaryType = {
  [IconTypes.LOGO_OUTLINED]: LogoIcon as unknown as React.FunctionComponent<
    React.SVGAttributes<SVGElement>
  >,
  [IconTypes.LOGO_OUTLINED_V2]:
    LogoIconV2 as unknown as React.FunctionComponent<
      React.SVGAttributes<SVGElement>
    >,
  [IconTypes.MENU_OUTLINED]: MenuIcon as unknown as React.FunctionComponent<
    React.SVGAttributes<SVGElement>
  >,
  [IconTypes.TODOIST_OUTLINED]:
    TodoistIcon as unknown as React.FunctionComponent<
      React.SVGAttributes<SVGElement>
    >,
  [IconTypes.TELEGRAM_OUTLINED]:
    TelegramIcon as unknown as React.FunctionComponent<
      React.SVGAttributes<SVGElement>
    >,
};
export const enum IconSizes {
  SMALL,
  MEDIUM,
  LARGE,
}

interface IconSize {
  width: number;
  stroke: number;
}

export const IconSizeValues: Record<IconSizes, IconSize> = {
  [IconSizes.SMALL]: {
    width: 16,
    stroke: 1,
  },
  [IconSizes.MEDIUM]: {
    width: 24,
    stroke: 1.5,
  },
  [IconSizes.LARGE]: {
    width: 36,
    stroke: 2.25,
  },
};

export interface IconSizeWithHeight extends IconSize {
  height?: number;
}

export interface IResponsiveSizes {
  base?: IconSizeWithHeight;
  md?: IconSizeWithHeight;
  lg?: IconSizeWithHeight;
  xl?: IconSizeWithHeight;
  xxl?: IconSizeWithHeight;
}

export const enum IconRotation {
  DEG_0,
  DEG_45,
  DEG_90,
  DEG_180,
  DEG_270,
}

export const IconRotationClasses: Record<IconRotation, string> = {
  [IconRotation.DEG_0]: "rotate-0",
  [IconRotation.DEG_45]: "rotate-45",
  [IconRotation.DEG_90]: "rotate-90",
  [IconRotation.DEG_180]: "rotate-180",
  [IconRotation.DEG_270]: "rotate-270",
};
