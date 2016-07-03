#ifndef THREAD_POOL_H
#define THREAD_POOL_H

#include <vector>
#include <queue>
#include <memory>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <future>
#include <functional>
#include <stdexcept>

#endif

class ThreadPool
{
public:
	ThreadPool(size_t);

	template<class F, class... Args>
	auto enqueue(F&& f, Args&&... args)->std::future<typename std::result_of;

	~ThreadPool();
private:

};