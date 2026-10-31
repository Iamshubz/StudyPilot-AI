package level1;
import java.util.*;
public class swappin {
public static void main(String[]args){
  Scanner sc = new Scanner(System.in);
  int a, b;
  
  System.out.println("enetr you frist value:");
  a = sc.nextInt();
  
  System.out.println("Enter your second value:");
  b = sc.nextInt();

  a= a+b;
  b= a-b;
  a= a-b;
    
  System.out.println("now your first value is:"+a);
  System.out.println("your second valude is:"+b);
  sc.close();
}   
}
