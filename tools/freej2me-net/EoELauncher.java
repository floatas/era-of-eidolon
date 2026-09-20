import org.recompile.freej2me.AWTGUI;

/**
 * FreeJ2ME launcher that remaps the phone keypad to the top-row number keys.
 *
 * Stock FreeJ2ME-Plus binds phone keys 0-9 to VK_NUMPAD0..9 (AWTGUI.inputKeycodes),
 * so on a laptop without a numeric keypad there is no way to press them — which
 * makes multi-tap text entry impossible. Era of Eidolon enters hero names with
 * classic multi-tap (c.java:7: "abc2", "def3", ...), so this is the difference
 * between being able to create a character and not.
 *
 * inputKeycodes is a public static array and is not persisted in FreeJ2ME's
 * config, so setting it before main() runs is enough.
 *
 * Index order (from AWTGUI): softL softR UP LEFT FIRE RIGHT DOWN
 *                            7 8 9 4 5 6 1 2 3 star 0 hash A B C D
 */
public class EoELauncher {
   public static void main(String[] args) throws Exception {
      AWTGUI.inputKeycodes = new int[] {
         81,  // Q      soft left
         87,  // W      soft right
         38,  // Up
         37,  // Left
         10,  // Enter  fire
         39,  // Right
         40,  // Down
         55, 56, 57,  // 7 8 9   (was NUMPAD7/8/9)
         52, 53, 54,  // 4 5 6   (was NUMPAD4/5/6)
         49, 50, 51,  // 1 2 3   (was NUMPAD1/2/3)
         69,  // E      star
         48,  // 0      (was NUMPAD0)
         82,  // R      hash
         65,  // A
         32,  // Space
         67,  // C
         88,  // X
      };
      org.recompile.freej2me.FreeJ2ME.main(args);
   }
}
