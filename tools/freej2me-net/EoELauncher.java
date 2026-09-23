import java.awt.KeyboardFocusManager;
import java.awt.event.KeyEvent;

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
      // WASD joins the arrow keys. Q is sent as Enter, the centre button:
      // confirm, Choose action, and the fight bar. The clear button is Z.
      // E is bound directly as the right soft key below. Rewriting the
      // keystroke in this dispatcher does not reach FreeJ2ME on macOS, so
      // E cannot be aliased onto F here.
      KeyboardFocusManager.getCurrentKeyboardFocusManager().addKeyEventDispatcher(e -> {
         int code = e.getKeyCode();
         int mapped = code;
         if (code == KeyEvent.VK_W) mapped = KeyEvent.VK_UP;
         else if (code == KeyEvent.VK_A) mapped = KeyEvent.VK_LEFT;
         else if (code == KeyEvent.VK_S) mapped = KeyEvent.VK_DOWN;
         else if (code == KeyEvent.VK_D) mapped = KeyEvent.VK_RIGHT;
         else if (code == KeyEvent.VK_Q) mapped = KeyEvent.VK_ENTER;
         if (mapped != code) {
            e.setKeyCode(mapped);
            e.setKeyChar(KeyEvent.CHAR_UNDEFINED);
         }
         return false;
      });
      AWTGUI.inputKeycodes = new int[] {
         81,  // soft left (Q is remapped to Enter above)
         69,  // E      soft right, opens the main menu on the map
         38,  // Up
         37,  // Left
         10,  // Enter  fire
         39,  // Right
         40,  // Down
         55, 56, 57,  // 7 8 9   (was NUMPAD7/8/9)
         52, 53, 54,  // 4 5 6   (was NUMPAD4/5/6)
         49, 50, 51,  // 1 2 3   (was NUMPAD1/2/3)
         192, // `      star (E is the right soft key)
         48,  // 0      (was NUMPAD0)
         82,  // R      hash
         90,  // Z      clear (A is left)
         32,  // Space
         67,  // C
         88,  // X
      };
      org.recompile.freej2me.FreeJ2ME.main(args);
   }
}
