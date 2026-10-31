package level1;
import java.util.*;
public class subject {
        public static void main(String[]args){
            Scanner sc = new Scanner(System.in);
            int m1,m2,m3,m4,m5;
            int total;
            double average;

        System.out.print("enetr marks of m1:");
        m1 =sc.nextInt();

        System.out.print("enter your m2 subject marks:");
        m2=sc.nextInt();

        System.out.print("enter your m3 subject marks:");
           m3=sc.nextInt();

            System.out.print("enter your m4 subject marks:");
               m4=sc.nextInt();

        System.out.print("enter your m5 subject marks:");
           m5=sc.nextInt();

           total=m1+m2+m3+m4+m5;
           average=total/5.0;

                System.out.println("your total marks is :"+total);
                System.out.println("your marks avarage is:"+average);
           sc.close();

}  

}
