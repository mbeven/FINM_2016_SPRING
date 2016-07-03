#include <mutex>
#include <thread>
#include <queue>
#include <iostream>
#include <condition_variable>

using std::thread;

template <typename T>
class buffer 
{
public:
    buffer(int capacity)  
		: capacity_(capacity) 
	{}

    void push(T data) //push operation to add an item
	{
        std::unique_lock<std::mutex> lock(buffer_lock); //buffer is a shared resource

        not_full.wait(lock, [this]() //see whether it is not full.  if full, wait.. otherwise add item
			{ 
				return buffer_.size() != capacity_; //check to see if buffer is not full 
			});

		buffer_.push(data);
        not_empty.notify_one();
    }

    int pop()
	{
        std::unique_lock<std::mutex> lock(buffer_lock);

        not_empty.wait(lock, [this]()
			{
				return !buffer_.empty(); //check to see if buffer is not empty -- i.e. there's data in the buffer 
			});
 
		T data = buffer_.front();
		buffer_.pop();
        not_full.notify_one();
		return data;
    }

private:
	std::queue<T> buffer_;
    int capacity_;

    std::mutex buffer_lock;

    std::condition_variable not_full;
    std::condition_variable not_empty;
};

void ConsumerTask(int id, buffer<int>& buffer)
{
    while(true)
	{
        int value = buffer.pop();
        std::cout << "Consumer " << id << ": consumed item: " << value << std::endl;
		//consumer takes x ms to consume an item
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));      
	}
}

void ProducerTask(int id, buffer<int>& buffer)
{
    int item = 0;
	while(true)
	{
		//producer takes y ms to produce an item
		std::this_thread::sleep_for(std::chrono::milliseconds(10));

        buffer.push(++item);
        std::cout << "Producer " << id << ": produced item: " << item << std::endl;
    }
}

int main()
{
    buffer<int> buffer(3);

    thread c1(ConsumerTask, 0, std::ref(buffer));
    //thread c2(ConsumerTask, 1, std::ref(buffer));
    //thread c3(ConsumerTask, 2, std::ref(buffer));
    thread p1(ProducerTask, 0, std::ref(buffer));
    //thread p2(ProducerTask, 1, std::ref(buffer));
	//thread p3(ProducerTask, 2, std::ref(buffer));

    c1.join();
    //c2.join();
    //c3.join();
    p1.join();
    //p2.join();
	//p3.join();

}



