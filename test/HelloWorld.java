import java.io.Serializable;

public class HelloWorld implements Serializable {
  public int m_public;
  protected int m_protected;
  private int m_private;
  static int m_static;
  int m_default;


  public static void main (String[] argv) {
    System.out.println("Hello World!");
    System.out.println(1337);
    System.out.println(13.37);
    System.out.println(13.37f);
    System.out.println(1.1f);
    return;
  }
}
