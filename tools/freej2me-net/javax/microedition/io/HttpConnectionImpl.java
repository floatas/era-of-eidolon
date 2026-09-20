package javax.microedition.io;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

/**
 * Real networking replacement for FreeJ2ME-Plus's stubbed HttpConnectionImpl.
 *
 * The stock class in freej2me.jar never touches the network: connect() only
 * logs, getResponseCode() returns a hardcoded 200, openOutputStream() discards
 * into a ByteArrayOutputStream and openInputStream() hands back the literal
 * bytes "resource://!blank". Any MIDlet that speaks a real protocol therefore
 * fails its first sanity check and retries forever.
 *
 * Put this class ahead of freej2me.jar on the classpath and it shadows the
 * stub. Same package, same package-private signature, same interfaces; only
 * the transport is real.
 *
 * Deliberately permissive: no redirects (the MIDlet handles its own), no
 * caching, short timeouts, and IO failures surface to the MIDlet as they would
 * on a real handset.
 */
class HttpConnectionImpl implements HttpConnection, com.nttdocomo.io.HttpConnection {
   Map<String, String> requestProperty = new HashMap<>();
   private String url;
   private String requestMethod = "GET";

   private final ByteArrayOutputStream requestBody = new ByteArrayOutputStream();
   private HttpURLConnection conn;
   private byte[] responseBody;
   private int responseCode = -1;
   private String responseMessage = "";
   private boolean performed = false;

   public HttpConnectionImpl(String var1) {
      this.url = var1;
   }

   /** Runs the request exactly once, lazily, on first read of any result. */
   private synchronized void perform() {
      if (performed) {
         return;
      }
      performed = true;
      try {
         conn = (HttpURLConnection) new URL(url).openConnection();
         conn.setInstanceFollowRedirects(false);
         conn.setUseCaches(false);
         conn.setConnectTimeout(10000);
         conn.setReadTimeout(30000);
         conn.setRequestMethod(requestMethod == null ? "GET" : requestMethod);
         for (Map.Entry<String, String> e : requestProperty.entrySet()) {
            conn.setRequestProperty(e.getKey(), e.getValue());
         }
         byte[] out = requestBody.toByteArray();
         if (out.length > 0 || "POST".equalsIgnoreCase(requestMethod)) {
            conn.setDoOutput(true);
            conn.setFixedLengthStreamingMode(out.length);
            try (OutputStream os = conn.getOutputStream()) {
               os.write(out);
            }
         }
         responseCode = conn.getResponseCode();
         responseMessage = String.valueOf(conn.getResponseMessage());
         InputStream in = responseCode >= 400 ? conn.getErrorStream() : conn.getInputStream();
         ByteArrayOutputStream buf = new ByteArrayOutputStream();
         if (in != null) {
            byte[] chunk = new byte[8192];
            int n;
            while ((n = in.read(chunk)) > 0) {
               buf.write(chunk, 0, n);
            }
            in.close();
         }
         responseBody = buf.toByteArray();
         System.out.println("[net] " + requestMethod + " " + url
               + " -> " + responseCode + " (" + out.length + "B up, "
               + responseBody.length + "B down)");
      } catch (Exception e) {
         responseCode = responseCode < 0 ? 500 : responseCode;
         responseBody = new byte[0];
         System.out.println("[net] " + url + " FAILED: " + e);
      }
   }

   public String getURL() {
      return this.url;
   }

   public String getProtocol() {
      return this.url.split(":")[0];
   }

   public String getHost() {
      try {
         return new URL(url).getHost();
      } catch (Exception e) {
         return "";
      }
   }

   public String getFile() {
      try {
         return new URL(url).getFile();
      } catch (Exception e) {
         return "";
      }
   }

   public String getRef() {
      try {
         String r = new URL(url).getRef();
         return r == null ? "" : r;
      } catch (Exception e) {
         return "";
      }
   }

   public String getQuery() {
      try {
         String q = new URL(url).getQuery();
         return q == null ? "" : q;
      } catch (Exception e) {
         return "";
      }
   }

   public int getPort() {
      try {
         int p = new URL(url).getPort();
         return p == -1 ? 80 : p;
      } catch (Exception e) {
         return 80;
      }
   }

   public String getRequestMethod() {
      return this.requestMethod;
   }

   public void setRequestMethod(String var1) {
      this.requestMethod = var1;
   }

   public String getRequestProperty(String var1) {
      return this.requestProperty.get(var1);
   }

   public void setRequestProperty(String var1, String var2) {
      this.requestProperty.put(var1, var2);
   }

   public void connect() throws IOException {
      perform();
   }

   public int getResponseCode() {
      perform();
      return responseCode;
   }

   public String getResponseMessage() {
      perform();
      return responseMessage;
   }

   public long getExpiration() {
      perform();
      return conn == null ? 0L : conn.getExpiration();
   }

   public long getDate() {
      perform();
      return conn == null ? 0L : conn.getDate();
   }

   public long getLastModified() {
      perform();
      return conn == null ? 0L : conn.getLastModified();
   }

   public String getHeaderField(String var1) {
      perform();
      return conn == null ? null : conn.getHeaderField(var1);
   }

   public int getHeaderFieldInt(String var1, int var2) {
      perform();
      return conn == null ? var2 : conn.getHeaderFieldInt(var1, var2);
   }

   public long getHeaderFieldDate(String var1, long var2) {
      perform();
      return conn == null ? var2 : conn.getHeaderFieldDate(var1, var2);
   }

   public String getHeaderField(int var1) {
      perform();
      return conn == null ? null : conn.getHeaderField(var1);
   }

   public String getHeaderFieldKey(int var1) {
      perform();
      return conn == null ? null : conn.getHeaderFieldKey(var1);
   }

   public void close() {
      if (conn != null) {
         conn.disconnect();
      }
   }

   public String getType() {
      perform();
      return conn == null ? null : conn.getContentType();
   }

   public String getEncoding() {
      perform();
      return conn == null ? null : conn.getContentEncoding();
   }

   public long getLength() {
      perform();
      return responseBody == null ? 0L : responseBody.length;
   }

   public DataInputStream openDataInputStream() throws UnsupportedEncodingException {
      return new DataInputStream(this.openInputStream());
   }

   public InputStream openInputStream() throws UnsupportedEncodingException {
      perform();
      return new ByteArrayInputStream(responseBody == null ? new byte[0] : responseBody);
   }

   public DataOutputStream openDataOutputStream() {
      return new DataOutputStream(this.openOutputStream());
   }

   public OutputStream openOutputStream() {
      return requestBody;
   }
}
