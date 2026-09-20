package javax.microedition.io;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

/**
 * Real HTTP for freej2me-web.
 *
 * The upstream web build has no HTTP at all — its Connector.open() throws
 * ConnectionNotFoundException for anything that is not sms://. This adds a
 * working javax.microedition.io.HttpConnection on top of java.net, which
 * CheerpJ maps onto the browser's fetch.
 *
 * Because that mapping is subject to the browser's origin rules, the page and
 * the server must share scheme, host and port. Era of Eidolon's MIDlets take a
 * `Relay` property from the jar manifest, so pointing it at a same-origin path
 * is enough — no CORS, no proxy.
 *
 * The request body is buffered and the exchange performed lazily on the first
 * read of any result, because MIDlets write their body before ever asking for
 * a response code.
 */
public class HttpConnectionImpl implements HttpConnection {
    private final Map<String, String> requestProperty = new HashMap<String, String>();
    private final String url;
    private String requestMethod = "GET";

    private final ByteArrayOutputStream requestBody = new ByteArrayOutputStream();
    private HttpURLConnection conn;
    private byte[] responseBody;
    private int responseCode = -1;
    private String responseMessage = "";
    private boolean performed = false;

    public HttpConnectionImpl(String url) {
        this.url = url;
    }

    private synchronized void perform() {
        if (performed) {
            return;
        }
        performed = true;
        try {
            conn = (HttpURLConnection) new URL(url).openConnection();
            conn.setInstanceFollowRedirects(false);
            conn.setUseCaches(false);
            conn.setRequestMethod(requestMethod == null ? "GET" : requestMethod);
            for (Map.Entry<String, String> e : requestProperty.entrySet()) {
                conn.setRequestProperty(e.getKey(), e.getValue());
            }
            byte[] out = requestBody.toByteArray();
            if (out.length > 0 || "POST".equalsIgnoreCase(requestMethod)) {
                conn.setDoOutput(true);
                OutputStream os = conn.getOutputStream();
                os.write(out);
                os.close();
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
            System.out.println("[net] " + requestMethod + " " + url + " -> " + responseCode
                    + " (" + out.length + "B up, " + responseBody.length + "B down)");
        } catch (Exception e) {
            responseCode = responseCode < 0 ? 500 : responseCode;
            responseBody = new byte[0];
            System.out.println("[net] " + url + " FAILED: " + e);
        }
    }

    public String getURL() { return url; }

    public String getProtocol() { return url.split(":")[0]; }

    public String getHost() {
        try { return new URL(url).getHost(); } catch (Exception e) { return ""; }
    }

    public String getFile() {
        try { return new URL(url).getFile(); } catch (Exception e) { return ""; }
    }

    public String getRef() {
        try { String r = new URL(url).getRef(); return r == null ? "" : r; }
        catch (Exception e) { return ""; }
    }

    public String getQuery() {
        try { String q = new URL(url).getQuery(); return q == null ? "" : q; }
        catch (Exception e) { return ""; }
    }

    public int getPort() {
        try { int p = new URL(url).getPort(); return p == -1 ? 80 : p; }
        catch (Exception e) { return 80; }
    }

    public String getRequestMethod() { return requestMethod; }

    public void setRequestMethod(String m) { requestMethod = m; }

    public String getRequestProperty(String k) { return requestProperty.get(k); }

    public void setRequestProperty(String k, String v) { requestProperty.put(k, v); }

    public int getResponseCode() { perform(); return responseCode; }

    public String getResponseMessage() { perform(); return responseMessage; }

    public long getExpiration() { perform(); return conn == null ? 0L : conn.getExpiration(); }

    public long getDate() { perform(); return conn == null ? 0L : conn.getDate(); }

    public long getLastModified() { perform(); return conn == null ? 0L : conn.getLastModified(); }

    public String getHeaderField(String k) { perform(); return conn == null ? null : conn.getHeaderField(k); }

    public int getHeaderFieldInt(String k, int d) { perform(); return conn == null ? d : conn.getHeaderFieldInt(k, d); }

    public long getHeaderFieldDate(String k, long d) { perform(); return conn == null ? d : conn.getHeaderFieldDate(k, d); }

    public String getHeaderField(int i) { perform(); return conn == null ? null : conn.getHeaderField(i); }

    public String getHeaderFieldKey(int i) { perform(); return conn == null ? null : conn.getHeaderFieldKey(i); }

    public String getType() { perform(); return conn == null ? null : conn.getContentType(); }

    public String getEncoding() { perform(); return conn == null ? null : conn.getContentEncoding(); }

    public long getLength() { perform(); return responseBody == null ? 0L : responseBody.length; }

    public void close() { if (conn != null) { conn.disconnect(); } }

    public DataInputStream openDataInputStream() {
        return new DataInputStream(openInputStream());
    }

    public InputStream openInputStream() {
        perform();
        return new ByteArrayInputStream(responseBody == null ? new byte[0] : responseBody);
    }

    public DataOutputStream openDataOutputStream() {
        return new DataOutputStream(openOutputStream());
    }

    public OutputStream openOutputStream() {
        return requestBody;
    }
}
