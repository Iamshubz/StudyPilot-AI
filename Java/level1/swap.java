package level1;
import java.util.*;
public class swap {
    public static void main(String[]args){
        Scanner sc = new Scanner(System.in);
        int a, b, temp;
    System.out.print("enetr you first value:");
    a = sc.nextInt();
    System.err.print("enter your second number:");
    b = sc.nextInt();
    temp=a;
    a=b;
    b=temp;
    System.out.println("after swapping:");
    System.out.println("your first value became="+a);
    System.out.println("second value became="+b);
    sc.close();

    }
}
