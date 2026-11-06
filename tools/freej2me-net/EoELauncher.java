import java.awt.KeyboardFocusManager;
import java.awt.event.KeyEvent;

import org.recompile.freej2me.AWTGUI;
import org.recompile.mobile.MIDletLoader;
import org.recompile.mobile.MobilePlatform;

/**
 * Desktop keys for the phone emulator.
 *
 * Chapters keep WASD for walking and Q for the centre button. E is the right
 * soft key, and Escape is sent as that same key.
 *
 * The online jars (poker, blackjack, Orumant, Dagonar) take a normal keyboard.
 * Arrow keys move, Enter confirms, Escape goes back, and letter keys type.
 * Backspace deletes. Those letters are not also bound as phone buttons, or
 * the emulator would swallow them before the text box saw them.
 *
 * Index order (from AWTGUI): softL softR UP LEFT FIRE RIGHT DOWN
 *                            7 8 9 4 5 6 1 2 3 star 0 hash CLR, then extras.
 */
public class EoELauncher {
   static boolean onlineJar(String[] args) {
      if (args == null) {
         return false;
      }
      for (int i = 0; i < args.length; i++) {
         if (args[i] == null) {
            continue;
         }
         String name = args[i].toLowerCase();
         if (name.contains("badaz") || name.contains("blackjack")
               || name.contains("orumant") || name.contains("dagonar")) {
            return true;
         }
      }
      return false;
   }

   public static void main(String[] args) throws Exception {
      final boolean online = onlineJar(args);
      KeyboardFocusManager.getCurrentKeyboardFocusManager().addKeyEventDispatcher(e -> {
         int id = e.getID();
         if (id != KeyEvent.KEY_PRESSED && id != KeyEvent.KEY_RELEASED) {
            return false;
         }
         int code = e.getKeyCode();
         if (!online) {
            // setKeyCode on this event is what WASD already uses. A second
            // KeyEvent built here does not reach FreeJ2ME on macOS.
            int mapped = code;
            if (code == KeyEvent.VK_W) mapped = KeyEvent.VK_UP;
            else if (code == KeyEvent.VK_A) mapped = KeyEvent.VK_LEFT;
            else if (code == KeyEvent.VK_S) mapped = KeyEvent.VK_DOWN;
            else if (code == KeyEvent.VK_D) mapped = KeyEvent.VK_RIGHT;
            else if (code == KeyEvent.VK_Q) mapped = KeyEvent.VK_ENTER;
            else if (code == KeyEvent.VK_ESCAPE) mapped = KeyEvent.VK_E;
            if (mapped != code) {
               e.setKeyCode(mapped);
               e.setKeyChar(KeyEvent.CHAR_UNDEFINED);
            }
            return false;
         }
         if (code == KeyEvent.VK_UP || code == KeyEvent.VK_DOWN
               || code == KeyEvent.VK_LEFT || code == KeyEvent.VK_RIGHT
               || code == KeyEvent.VK_ENTER || code == KeyEvent.VK_ESCAPE
               || code == KeyEvent.VK_BACK_SPACE) {
            return false;
         }
         char ch = e.getKeyChar();
         // An unshifted digit still walks menus. Shift-1 is '!' and is typed.
         if (ch >= '0' && ch <= '9' && code >= KeyEvent.VK_0 && code <= KeyEvent.VK_9) {
            return false;
         }
         if (ch < 32 || ch > 126 || !MIDletLoader.MIDletSelected) {
            return false;
         }
         try {
            if (id == KeyEvent.KEY_PRESSED) {
               MobilePlatform.keyPressed(ch);
            } else {
               MobilePlatform.keyReleased(ch);
            }
         } catch (Throwable ignored) {
            return false;
         }
         return true;
      });
      if (online) {
         AWTGUI.inputKeycodes = new int[] {
            113, // F2     left soft. Q has to type.
            27,  // Escape right soft, the back key
            38,  // Up
            37,  // Left
            10,  // Enter  confirm
            39,  // Right
            40,  // Down
            55, 56, 57,
            52, 53, 54,
            49, 50, 51,
            192, // `
            48,  // 0
            114, // F3     hash. R has to type.
            8,   // Backspace
            32,  // Space  (FreeJ2ME does not forward this slot)
            67,  // C
            88,  // X
         };
      } else {
         AWTGUI.inputKeycodes = new int[] {
            81,  // soft left (Q is remapped to Enter above)
            69,  // E      soft right, opens the main menu on the map
            38,  // Up
            37,  // Left
            10,  // Enter  fire
            39,  // Right
            40,  // Down
            55, 56, 57,  // 7 8 9
            52, 53, 54,  // 4 5 6
            49, 50, 51,  // 1 2 3
            192, // `      star
            48,  // 0
            82,  // R      hash
            90,  // Z      clear
            32,  // Space
            67,  // C
            88,  // X
         };
      }
      org.recompile.freej2me.FreeJ2ME.main(args);
   }
}
